#!/usr/bin/env python3
"""
backend/middleware/stream_shield.py
Sovereign Stream Shield — Traffic Shaping + Padding + No-Compression
Protected under HB 001 §1(5) • SNH-wrapped • Registry-logged • Revocable
"""

import os
import random
import asyncio
import json
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Sovereign stack
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

from backend.config import (
    PAD_MIN_MS, PAD_MAX_MS, PAD_MIN_BYTES, PAD_MAX_BYTES,
    DISABLE_COMPRESSION_PATHS
)

gtc = GTCSovereignEngine()
observer = MetaObserver()

def pad_bytes(raw: bytes, pad_len: int) -> bytes:
    """Sovereign body padding — random bytes to blunt size analysis."""
    padding = os.urandom(pad_len)
    return raw + padding

async def _sleep_ms(ms: int):
    await asyncio.sleep(ms / 1000.0)

class StreamShieldMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path

        # Strip compression hints on protected paths
        if path in DISABLE_COMPRESSION_PATHS:
            headers = list(request.scope.get("headers", []))
            headers = [(k, v) for k, v in headers if k.lower() != b"accept-encoding"]
            request.scope["headers"] = tuple(headers)

        resp = await call_next(request)

        if path not in DISABLE_COMPRESSION_PATHS:
            return resp

        # === SOVEREIGN HARDENING ===
        # 1. Force identity (no compression)
        resp.headers["Content-Encoding"] = "identity"
        resp.headers["X-Compression-Blocked"] = "1"
        resp.headers["Cache-Control"] = "no-store"

        # 2. Jittered latency
        delay_ms = random.randint(PAD_MIN_MS, PAD_MAX_MS)
        await _sleep_ms(delay_ms)

        # 3. Body padding
        raw = await resp.body()
        pad_len = random.randint(PAD_MIN_BYTES, PAD_MAX_BYTES)
        padded = pad_bytes(raw, pad_len)

        new_resp = Response(
            content=padded,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.media_type or "application/octet-stream",
        )
        new_resp.headers["X-Pad-Latency-Ms"] = str(delay_ms)
        new_resp.headers["X-Pad-Bytes"] = str(pad_len)

        # Sovereign receipt + logging
        receipt = Handshake.createReceipt(None, "STREAM-SHIELD", {
            "path": path,
            "delay_ms": delay_ms,
            "pad_bytes": pad_len,
            "original_size": len(raw),
            "padded_size": len(padded)
        })
        gtc.allocate_fireseed("session-τ-001", 0.02, note="Stream Shield Receipt")
        observer.intercept_response(json.dumps(receipt))

        return new_resp