#!/usr/bin/env python3
"""
backend/websocket_bridge.py
Real-time resonance streaming over WebSockets
NVIDIA + OpenAI + local embeddings • per-token Glyph triggers
"""

import asyncio
import websockets
from backend.embeddings import text_to_embedding
from src.gtc_sovereign_engine import GTCSovereignEngine
from com.landback.gibberlink.glyph_parser import GlyphParser

gtc = GTCSovereignEngine()

async def resonance_handler(websocket):
    async for message in websocket:
        emb = text_to_embedding(message)
        score = float(np.mean(np.abs(emb)))
        if score >= 0.55:
            GlyphParser.parseAndProcess(f"RESONANCE-WEBSOCKET-{score:.3f}", None)
        await websocket.send(json.dumps({"token": message, "resonance": score}))

async def start_websocket_server():
    async with websockets.serve(resonance_handler, "0.0.0.0", 8765):
        print("🔥 Sovereign WebSocket Bridge live on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever