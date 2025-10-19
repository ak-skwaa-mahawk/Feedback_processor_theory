#!/usr/bin/env python3
"""
Feedback Processor Theory - WebSocket Server
Multi-LLM streaming with resonance analysis
"""

import asyncio
import websockets
import json
import os
import logging
from datetime import datetime
from typing import Dict, Set
import signal
import base64
import traceback

from llm_clients import NVIDIAClient, GPTClient, ClaudeClient
from embeddings import text_to_embedding_openai, audio_bytes_to_embedding_openai
from session_manager import SessionManager
from resonance_engine import ResonanceEngine

# Configuration
HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
PORT = int(os.getenv("BACKEND_PORT", 8765))
ENABLE_EMBEDDINGS = os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true"
ENABLE_AUDIO = os.getenv("ENABLE_AUDIO", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", 100))

# Logging setup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
sessions: Dict[str, SessionManager] = {}
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

# Initialize LLM clients
try:
    nvidia_client = NVIDIAClient()
    logger.info("✓ NVIDIA client initialized")
except Exception as e:
    nvidia_client = None
    logger.warning(f"NVIDIA client unavailable: {e}")

try:
    gpt_client = GPTClient()
    logger.info("✓ OpenAI GPT client initialized")
except Exception as e:
    gpt_client = None
    logger.warning(f"GPT client unavailable: {e}")

try:
    claude_client = ClaudeClient()
    logger.info("✓ Claude client initialized")
except Exception as e:
    claude_client = None
    logger.warning(f"Claude client unavailable: {e}")

# Resonance engine
resonance_engine = ResonanceEngine()


async def handle_prompt(websocket, session: SessionManager, data: dict):
    """Handle text prompt with LLM streaming"""
    prompt = data.get("text", "")
    llm_choice = data.get("llm", "gpt").lower()
    
    if not prompt:
        await websocket.send(json.dumps({
            "type": "error",
            "message": "Empty prompt"
        }))
        return
    
    # Select client
    client = None
    if llm_choice == "gpt" and gpt_client:
        client = gpt_client
    elif llm_choice == "nvidia" and nvidia_client:
        client = nvidia_client
    elif llm_choice == "claude" and claude_client:
        client = claude_client
    
    if not client:
        await websocket.send(json.dumps({
            "type": "error",
            "message": f"LLM '{llm_choice}' not available"
        }))
        return
    
    logger.info(f"Session {session.session_id}: Processing prompt with {llm_choice}")
    
    try:
        # Stream tokens
        full_response = ""
        token_count = 0
        
        async for chunk in client.stream_response(prompt):
            token = chunk.get("token", "")
            if not token:
                continue
            
            full_response += token
            token_count += 1
            
            # Generate embedding for token (if enabled)
            token_emb = None
            if ENABLE_EMBEDDINGS and not DEMO_MODE:
                try:
                    token_emb = text_to_embedding_openai(token)
                    session.add_token_embedding(token_emb)
                except Exception as e:
                    logger.warning(f"Embedding failed: {e}")
            
            # Calculate resonance with audio
            resonance_score = 0.0
            if ENABLE_AUDIO and session.latest_audio_emb is not None and token_emb is not None:
                resonance_score = resonance_engine.calculate_resonance(
                    token_emb, 
                    session.latest_audio_emb
                )
            
            # Send token to client
            await websocket.send(json.dumps({
                "type": "token",
                "token": token,
                "llm": llm_choice,
                "resonance": resonance_score,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Small delay to prevent overwhelming client
            await asyncio.sleep(0.001)
        
        # Send completion
        session.add_message("assistant", full_response)
        await websocket.send(json.dumps({
            "type": "complete",
            "llm": llm_choice,
            "tokens": token_count,
            "message": full_response
        }))
        
        logger.info(f"Session {session.session_id}: Completed {token_count} tokens from {llm_choice}")
        
    except Exception as e:
        logger.error(f"Error streaming from {llm_choice}: {e}\n{traceback.format_exc()}")
        await websocket.send(json.dumps({
            "type": "error",
            "message": f"Streaming error: {str(e)}"
        }))


async def handle_audio_chunk(websocket, session: SessionManager, data: dict):
    """Handle audio chunk with transcription and embedding"""
    if not ENABLE_AUDIO:
        return
    
    audio_b64 = data.get("data", "")
    if not audio_b64:
        return
    
    try:
        # Decode audio bytes
        audio_bytes = base64.b64decode(audio_b64)
        
        # Generate audio embedding (transcribe + embed)
        if not DEMO_MODE:
            audio_emb = audio_bytes_to_embedding_openai(audio_bytes)
            session.latest_audio_emb = audio_emb
            
            # Analyze spectral properties
            spectral_data = resonance_engine.analyze_audio_spectrum(audio_bytes)
            
            await websocket.send(json.dumps({
                "type": "audio_processed",
                "embedding_size": len(audio_emb),
                "spectral": spectral_data,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            logger.debug(f"Session {session.session_id}: Audio chunk processed")
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        await websocket.send(json.dumps({
            "type": "error",
            "message": f"Audio processing error: {str(e)}"
        }))


async def handle_message(websocket, path):
    """Main WebSocket message handler"""
    session_id = None
    session = None
    
    try:
        # Register client
        connected_clients.add(websocket)
        
        # Create session
        session_id = f"sess_{datetime.utcnow().timestamp()}"
        session = SessionManager(session_id)
        sessions[session_id] = session
        
        logger.info(f"New connection: {session_id} (total: {len(connected_clients)})")
        
        # Send welcome
        await websocket.send(json.dumps({
            "type": "connected",
            "session_id": session_id,
            "features": {
                "embeddings": ENABLE_EMBEDDINGS,
                "audio": ENABLE_AUDIO,
                "demo_mode": DEMO_MODE
            },
            "available_llms": {
                "gpt": gpt_client is not None,
                "nvidia": nvidia_client is not None,
                "claude": claude_client is not None
            }
        }))
        
        # Message loop
        async for raw_message in websocket:
            try:
                msg = json.loads(raw_message)
                msg_type = msg.get("type", "")
                
                if msg_type == "prompt":
                    await handle_prompt(websocket, session, msg)
                
                elif msg_type == "audio_chunk":
                    await handle_audio_chunk(websocket, session, msg)
                
                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                
                elif msg_type == "get_history":
                    await websocket.send(json.dumps({
                        "type": "history",
                        "messages": session.get_history()
                    }))
                
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
            
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
            except Exception as e:
                logger.error(f"Error handling message: {e}\n{traceback.format_exc()}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Connection closed: {session_id}")
    
    except Exception as e:
        logger.error(f"Connection error: {e}\n{traceback.format_exc()}")
    
    finally:
        # Cleanup
        connected_clients.discard(websocket)
        if session_id and session_id in sessions:
            del sessions[session_id]
        logger.info(f"Disconnected: {session_id} (remaining: {len(connected_clients)})")


async def health_check(websocket, path):
    """Health check endpoint"""
    await websocket.send(json.dumps({
        "status": "healthy",
        "sessions": len(sessions),
        "clients": len(connected_clients),
        "timestamp": datetime.utcnow().isoformat()
    }))
    await websocket.close()


async def shutdown(signal, loop):
    """Graceful shutdown"""
    logger.info(f"Received exit signal {signal.name}...")
    
    # Close all connections
    tasks = []
    for ws in connected_clients:
        tasks.append(ws.close(1001, "Server shutting down"))
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # Clear sessions
    sessions.clear()
    
    logger.info("Shutdown complete")
    loop.stop()


async def main():
    """Start WebSocket server"""
    logger.info(f"Starting Harmonic Demo server on {HOST}:{PORT}")
    logger.info(f"Embeddings: {ENABLE_EMBEDDINGS} | Audio: {ENABLE_AUDIO} | Demo: {DEMO_MODE}")
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop))
        )
    
    # Start server
    async with websockets.serve(handle_message, HOST, PORT):
        logger.info(f"✓ Server ready at ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
# backend/server.py
# WebSocket server: launches LLM streams concurrently and broadcasts per-token messages
import os
import asyncio
import json
import websockets
from llm_clients import NVIDIAClient, GPTClient, ClaudeClient
from embeddings import text_to_embedding, audio_bytes_to_embedding
from trinity_utils import cosine_similarity, trinity_damping_scalar
import base64
import numpy as np

# Config
WS_HOST = "0.0.0.0"
WS_PORT = int(os.getenv("WS_PORT", 8765))

# Initialize clients (ensure env vars set)
nv_client = NVIDIAClient(api_key=os.getenv("NVAPI_KEY"))
gpt_client = GPTClient(api_key=os.getenv("GPT_KEY"))
claude_client = ClaudeClient(api_key=os.getenv("CLAUDE_KEY"))

# Keep track of connected WebSocket clients to broadcast visuals to frontends
CONNECTED = set()

# Token indices per session (to align visuals); we'll increment globally per session
class SessionState:
    def __init__(self):
        self.token_counter = 0
        self.latest_audio_emb = None

async def stream_llm_and_broadcast(prompt: str, llm_name: str, stream_gen, session: SessionState, websocket_broadcast):
    """
    Reads streaming tokens from stream_gen (generator yielding {"token":...})
    Computes embedding for each token, computes harmony against latest audio embedding (if present)
    Broadcasts a message for each token: { tokenIndex, llm, token, harmony, type: 'text' }
    """
    async for chunk in _async_generator_wrapper(stream_gen):
        token_text = chunk.get("token", "")
        token_text = token_text.strip()
        if not token_text:
            continue
        # compute embedding
        token_emb = text_to_embedding(token_text)
        # compute harmony vs audio if available
        harmony = 0.0
        if session.latest_audio_emb is not None:
            harmony = cosine_similarity(session.latest_audio_emb, token_emb)
            # apply damping
            harmony = trinity_damping_scalar(harmony, factor=0.5)
        # prepare message
        msg = {
            "tokenIndex": session.token_counter,
            "llm": llm_name,
            "token": token_text,
            "harmony": harmony,
            "type": "text"
        }
        session.token_counter += 1
        # broadcast to frontends
        await websocket_broadcast(json.dumps(msg))
        # small async yield to let other tasks run
        await asyncio.sleep(0)

async def _async_generator_wrapper(sync_gen):
    """
    Wrap a synchronous generator into an async generator.
    """
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)  # tiny yield

async def handle_ws(websocket, path):
    """
    Each connected frontend opens a websocket: it may send:
      - {"type":"start","prompt": "<initial prompt>"}  -> we start LLM streams for that prompt
      - {"type":"audio_chunk","data":"<base64 float32 PCM bytes>"} -> update session.latest_audio_emb
    We broadcast token events to *all* connected frontends so multiple viewers can see the same stream.
    """
    print("Client connected")
    CONNECTED.add(websocket)
    session = SessionState()
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get("type") == "start":
                prompt = msg.get("prompt", "Hello from Trinity harmonics demo")
                # Launch LLM streams concurrently for this prompt
                # Each stream is run in its own asyncio.create_task so we can read them concurrently
                asyncio.create_task(stream_llm_and_broadcast(prompt, "NVIDIA", nv_client.stream_response(prompt), session, broadcast))
                asyncio.create_task(stream_llm_and_broadcast(prompt, "GPT", gpt_client.stream_response(prompt), session, broadcast))
                asyncio.create_task(stream_llm_and_broadcast(prompt, "Claude", claude_client.stream_response(prompt), session, broadcast))
            elif msg.get("type") == "audio_chunk":
                # payload should be base64-encoded float32 PCM (as frontend sends)
                b64 = msg.get("data")
                if not b64:
                    continue
                raw_bytes = base64.b64decode(b64)
                # Convert bytes into numpy float32 vector
                try:
                    audio_np = np.frombuffer(raw_bytes, dtype=np.float32)
                except Exception:
                    # If buffer isn't float32, fragile fallback: ignore or attempt conversion
                    audio_np = None
                if audio_np is not None:
                    # compute audio embedding and store in session
                    session.latest_audio_emb = audio_bytes_to_embedding(raw_bytes)
                    # Optionally broadcast audio harmony value itself
                    # we compute a "self-harmony" (energy) for visualization
                    energy = float(np.linalg.norm(audio_np)) / (len(audio_np)+1e-12)
                    await broadcast(json.dumps({"type":"audio_energy","energy":energy}))
            else:
                # unknown message types can be ignored
                continue
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED.discard(websocket)
        print("Client disconnected")

async def broadcast(message: str):
    to_remove = []
    for ws in CONNECTED:
        try:
            await ws.send(message)
        except Exception:
            to_remove.append(ws)
    for r in to_remove:
        CONNECTED.discard(r)

def main():
    print(f"Starting WS server on ws://{WS_HOST}:{WS_PORT}")
    start_server = websockets.serve(handle_ws, WS_HOST, WS_PORT, max_queue=32)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()