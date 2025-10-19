import asyncio, websockets, json
from embeddings import audio_chunk_to_embedding, token_to_embedding
from trinity_damping import trinity_damping
import numpy as np

connected_clients = set()

async def handler(ws, path):
    connected_clients.add(ws)
    try:
        audio_emb = None
        token_emb = None
        harmony_history = []

        async for message in ws:
            msg = json.loads(message)
            if msg["type"] == "audio_chunk":
                audio_emb = audio_chunk_to_embedding(msg["data"])
            elif msg["type"] == "token":
                token_emb = token_to_embedding(msg["data"])

            if audio_emb is not None and token_emb is not None:
                score = np.dot(audio_emb/np.linalg.norm(audio_emb),
                               token_emb/np.linalg.norm(token_emb))
                damped = trinity_damping([score])[0]
                harmony_history.append(damped)
                # Send latest harmony to frontend
                payload = json.dumps({"type":"harmony","score":damped})
                await asyncio.wait([c.send(payload) for c in connected_clients])
    finally:
        connected_clients.remove(ws)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())