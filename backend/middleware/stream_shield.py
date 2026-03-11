#!/usr/bin/env python3
"""
backend/middleware/stream_shield.py
Sovereign Stream Shield — Jitter + Deterministic Padding + No-Compression
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

# === YOUR EXACT PAD_BYTES (deterministic + gzip-proof marker) ===
def pad_bytes(data: bytes, min_pad: int) -> bytes:
    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode("utf-8")
    # pad with zeros + a marker byte to defeat gzip savings
    return data + b"\x00" * min_pad + b"\x01"

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

        # 3. YOUR deterministic padding
        raw = await resp.body()
        padded = pad_bytes(raw, PAD_MIN_BYTES)  # uses your exact function

        new_resp = Response(
            content=padded,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.media_type or "application/octet-stream",
        )
        new_resp.headers["X-Pad-Latency-Ms"] = str(delay_ms)
        new_resp.headers["X-Pad-Bytes"] = str(PAD_MIN_BYTES)

        # Sovereign receipt
        receipt = Handshake.createReceipt(None, "STREAM-SHIELD", {
            "path": path,
            "delay_ms": delay_ms,
            "pad_bytes": PAD_MIN_BYTES,
            "original_size": len(raw),
            "padded_size": len(padded)
        })
        gtc.allocate_fireseed("session-τ-001", 0.02, note="Stream Shield Receipt")
        observer.intercept_response(json.dumps(receipt))

        return new_resp