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