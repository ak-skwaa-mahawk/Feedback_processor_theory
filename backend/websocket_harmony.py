#!/usr/bin/env python3
"""
backend/websocket_harmony.py
Real-time Sovereign Harmony Stream
Audio chunk + token embeddings → Trinity damping → broadcast
SNH + Registry + MetaObserver protected
"""

import asyncio
import websockets
import json
import numpy as np
from typing import Dict, Set

# Sovereign stack
from backend.embeddings import audio_chunk_to_embedding, token_to_embedding
from trinity_damping import trinity_damping
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

connected_clients: Set[websockets.WebSocketServerProtocol] = set()
gtc = GTCSovereignEngine()
observer = MetaObserver()

async def harmony_handler(websocket: websockets.WebSocketServerProtocol, path: str):
    connected_clients.add(websocket)
    try:
        audio_emb = None
        token_emb = None
        harmony_history = []

        async for message in websocket:
            msg = json.loads(message)
            if msg["type"] == "audio_chunk":
                audio_emb = audio_chunk_to_embedding(msg["data"])
            elif msg["type"] == "token":
                token_emb = token_to_embedding(msg["data"])

            if audio_emb is not None and token_emb is not None:
                # Sovereign resonance scoring
                score = np.dot(audio_emb / np.linalg.norm(audio_emb),
                               token_emb / np.linalg.norm(token_emb))
                damped = trinity_damping([score])[0]
                harmony_history.append(damped)

                # Broadcast to all clients
                payload = json.dumps({"type": "harmony", "score": float(damped)})
                await asyncio.wait([c.send(payload) for c in connected_clients if not c.closed])

                # Registry + Fireseed + Observer
                receipt = Handshake.createReceipt(None, "HARMONY-STREAM", {
                    "score": float(damped),
                    "history_length": len(harmony_history)
                })
                gtc.allocate_fireseed("session-τ-001", 0.05, note="Harmony Stream Receipt")
                observer.intercept_response(json.dumps(receipt))
    finally:
        connected_clients.discard(websocket)

async def start_harmony_server():
    async with websockets.serve(harmony_handler, "0.0.0.0", 8765):
        print("🔥 Sovereign Harmony WebSocket live on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_harmony_server())