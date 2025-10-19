# backend/server.py
import os
import asyncio
import json
import websockets
import base64
import numpy as np

from llm_clients import NVIDIAClient, GPTClient, ClaudeClient
from embeddings import text_to_embedding_openai, audio_bytes_to_embedding_openai
from trinity_utils import cosine_similarity, trinity_damping_scalar

WS_HOST = "0.0.0.0"
WS_PORT = int(os.getenv("WS_PORT", 8765))

nv_client = NVIDIAClient(api_key=os.getenv("NVAPI_KEY"))
gpt_client = GPTClient(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = ClaudeClient(api_key=os.getenv("CLAUDE_KEY"))

CONNECTED = set()

class SessionState:
    def __init__(self):
        self.token_counter = 0
        self.latest_audio_emb = None

async def _async_generator_wrapper(sync_gen):
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)

async def broadcast(message: str):
    to_remove = []
    for ws in CONNECTED:
        try:
            await ws.send(message)
        except Exception:
            to_remove.append(ws)
    for r in to_remove:
        CONNECTED.discard(r)

async def stream_llm_and_broadcast(prompt: str, llm_name: str, stream_gen, session: SessionState):
    async for chunk in _async_generator_wrapper(stream_gen):
        token_text = chunk.get("token", "").strip()
        if not token_text:
            continue
        token_emb = text_to_embedding_openai(token_text)
        harmony = 0.0
        if session.latest_audio_emb is not None:
            harmony = cosine_similarity(session.latest_audio_emb, token_emb)
            harmony = trinity_damping_scalar(harmony, factor=0.5)
        msg = {
            "tokenIndex": session.token_counter,
            "llm": llm_name,
            "token": token_text,
            "harmony": harmony,
            "type": "text"
        }
        session.token_counter += 1
        await broadcast(json.dumps(msg))
        await asyncio.sleep(0)

async def handle_ws(websocket, path):
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
                asyncio.create_task(stream_llm_and_broadcast(prompt, "NVIDIA", nv_client.stream_response(prompt), session))
                asyncio.create_task(stream_llm_and_broadcast(prompt, "GPT", gpt_client.stream_response(prompt), session))
                asyncio.create_task(stream_llm_and_broadcast(prompt, "Claude", claude_client.stream_response(prompt), session))
            elif msg.get("type") == "audio_chunk":
                b64 = msg.get("data")
                if not b64:
                    continue
                raw_bytes = base64.b64decode(b64)
                session.latest_audio_emb = audio_bytes_to_embedding_openai(raw_bytes)
                energy = float(np.linalg.norm(np.frombuffer(raw_bytes, dtype=np.float32))) / (len(raw_bytes)+1e-12)
                await broadcast(json.dumps({"type":"audio_energy","energy":energy}))
            else:
                continue
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED.discard(websocket)
        print("Client disconnected")

def main():
    print(f"Starting WS server on ws://{WS_HOST}:{WS_PORT}")
    start_server = websockets.serve(handle_ws, WS_HOST, WS_PORT, max_queue=32)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()