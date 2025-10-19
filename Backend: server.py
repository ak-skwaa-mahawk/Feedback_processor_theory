# backend/server.py
import asyncio, json, numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from llm_clients import NVIDIAClient, GPTClient, ClaudeClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize clients
nvidia = NVIDIAClient("YOUR_NVAPI_KEY")
gpt = GPTClient()
claude = ClaudeClient()

def get_embedding(text):
    vec = np.random.rand(128)
    return vec / np.linalg.norm(vec)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        message = json.loads(data)
        user_text = message.get("text", "")
        audio_embedding = np.array(message.get("audio_embedding", np.zeros(128)))

        # Compute user embedding
        user_embedding = get_embedding(user_text)
        fused_user = 0.5 * user_embedding + 0.5 * audio_embedding
        fused_user = fused_user / np.linalg.norm(fused_user)

        # Async tasks for multi-LLM streams
        async def stream_llm(client, name):
            for token in client.stream_response(user_text):
                token_emb = get_embedding(token)
                harmony = float(np.dot(fused_user, token_emb))
                await ws.send_text(json.dumps({
                    "llm": name,
                    "token": token,
                    "harmony": harmony
                }))

        await asyncio.gather(
            stream_llm(nvidia, "NVIDIA"),
            stream_llm(gpt, "GPT"),
            stream_llm(claude, "Claude")
        )