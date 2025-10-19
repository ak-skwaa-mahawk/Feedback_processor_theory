# backend/server.py
# Enhanced with cache stats, demo mode toggle, and status reporting
import os
import asyncio
import json
import websockets
import base64
import numpy as np

from llm_clients import NVIDIAClient, GPTClient, ClaudeClient
from embeddings import text_to_embedding_openai, audio_bytes_to_embedding_openai, get_cache_stats
from trinity_utils import cosine_similarity, trinity_damping_scalar

WS_HOST = "0.0.0.0"
WS_PORT = int(os.getenv("WS_PORT", 8765))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Initialize clients with error handling
clients = {}
try:
    clients["nvidia"] = NVIDIAClient(api_key=os.getenv("NVAPI_KEY"))
    print("✓ NVIDIA client initialized")
except Exception as e:
    print(f"⚠ NVIDIA client unavailable: {e}")

try:
    clients["gpt"] = GPTClient(api_key=os.getenv("OPENAI_API_KEY"))
    print("✓ GPT client initialized")
except Exception as e:
    print(f"⚠ GPT client unavailable: {e}")

try:
    clients["claude"] = ClaudeClient(api_key=os.getenv("CLAUDE_KEY"))
    print("✓ Claude client initialized")
except Exception as e:
    print(f"⚠ Claude client unavailable: {e}")

CONNECTED = set()

class SessionState:
    def __init__(self):
        self.token_counter = 0
        self.latest_audio_emb = None
        self.demo_mode = DEMO_MODE

async def _async_generator_wrapper(sync_gen):
    """Wrap sync generator for async iteration"""
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)

async def broadcast(message: str):
    """Send message to all connected clients"""
    to_remove = []
    for ws in CONNECTED:
        try:
            await ws.send(message)
        except Exception:
            to_remove.append(ws)
    for r in to_remove:
        CONNECTED.discard(r)

async def stream_llm_and_broadcast(prompt: str, llm_name: str, stream_gen, session: SessionState):
    """Stream LLM tokens with harmony calculation"""
    async for chunk in _async_generator_wrapper(stream_gen):
        token_text = chunk.get("token", "").strip()
        if not token_text:
            continue
        
        # Generate token embedding (cached)
        token_emb = text_to_embedding_openai(token_text)
        
        # Calculate harmony with audio
        harmony = 0.0
        if session.latest_audio_emb is not None:
            harmony = cosine_similarity(session.latest_audio_emb, token_emb)
            harmony = trinity_damping_scalar(harmony, factor=0.5)
        
        msg = {
            "tokenIndex": session.token_counter,
            "llm": llm_name,
            "token": token_text,
            "harmony": harmony,
            "type": "text",
            "demo_mode": session.demo_mode
        }
        session.token_counter += 1
        await broadcast(json.dumps(msg))
        await asyncio.sleep(0)
    
    # Send completion message
    await broadcast(json.dumps({
        "type": "completion",
        "llm": llm_name,
        "tokens": session.token_counter
    }))

async def handle_ws(websocket, path):
    """Main WebSocket handler"""
    print(f"Client connected (total: {len(CONNECTED) + 1})")
    CONNECTED.add(websocket)
    session = SessionState()
    
    # Send welcome message with status
    await websocket.send(json.dumps({
        "type": "connected",
        "demo_mode": session.demo_mode,
        "available_llms": list(clients.keys()),
        "cache_enabled": os.getenv("USE_EMBEDDING_CACHE", "true").lower() == "true"
    }))
    
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            
            msg_type = msg.get("type")
            
            # Start multi-LLM streaming
            if msg_type == "start":
                prompt = msg.get("prompt", "Hello from Trinity harmonics demo")
                
                # Start all available LLMs in parallel
                for llm_name, client in clients.items():
                    asyncio.create_task(
                        stream_llm_and_broadcast(
                            prompt, 
                            llm_name.upper(), 
                            client.stream_response(prompt), 
                            session
                        )
                    )
            
            # Handle audio chunk
            elif msg_type == "audio_chunk":
                b64 = msg.get("data")
                if not b64:
                    continue
                
                try:
                    raw_bytes = base64.b64decode(b64)
                    session.latest_audio_emb = audio_bytes_to_embedding_openai(raw_bytes)
                    
                    # Calculate audio energy
                    audio_array = np.frombuffer(raw_bytes, dtype=np.float32)
                    energy = float(np.linalg.norm(audio_array)) / (len(audio_array) + 1e-12)
                    
                    await broadcast(json.dumps({
                        "type": "audio_energy",
                        "energy": energy,
                        "demo_mode": session.demo_mode
                    }))
                except Exception as e:
                    print(f"Audio processing error: {e}")
            
            # Toggle demo mode
            elif msg_type == "toggle_demo":
                session.demo_mode = not session.demo_mode
                os.environ["DEMO_MODE"] = "true" if session.demo_mode else "false"
                
                await broadcast(json.dumps({
                    "type": "demo_toggled",
                    "demo_mode": session.demo_mode
                }))
            
            # Get cache statistics
            elif msg_type == "get_stats":
                stats = get_cache_stats()
                await websocket.send(json.dumps({
                    "type": "stats",
                    "cache": stats,
                    "session": {
                        "tokens_processed": session.token_counter,
                        "has_audio": session.latest_audio_emb is not None
                    }
                }))
            
            # Ping/pong
            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED.discard(websocket)
        print(f"Client disconnected (remaining: {len(CONNECTED)})")

def main():
    """Start WebSocket server"""
    print(f"\n{'='*50}")
    print(f"Trinity Harmonics Server")
    print(f"{'='*50}")
    print(f"WebSocket: ws://{WS_HOST}:{WS_PORT}")
    print(f"Demo Mode: {DEMO_MODE}")
    print(f"Available LLMs: {', '.join(clients.keys())}")
    print(f"{'='*50}\n")
    
    start_server = websockets.serve(handle_ws, WS_HOST, WS_PORT, max_queue=32)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()