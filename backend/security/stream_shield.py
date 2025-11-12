import random
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from backend.config import (
    PAD_MIN_MS, PAD_MAX_MS, PAD_MIN_BYTES, PAD_MAX_BYTES, DISABLE_COMPRESSION_PATHS
)
from .util import pad_bytes

async def _sleep_ms(ms: int):
    import asyncio
    await asyncio.sleep(ms / 1000.0)

class StreamShieldMiddleware(BaseHTTPMiddleware):
    """
    Adds jittered latency + size padding on sensitive routes to blunt traffic analysis.
    Also forces identity (no compression) on those routes.
    """
    async def dispatch(self, request, call_next):
        path = request.url.path

        # strip client compression hints; we force identity later
        if path in DISABLE_COMPRESSION_PATHS:
            request.scope["headers"] = tuple(
                (k, v) for (k, v) in request.scope.get("headers", [])
                if k.lower() != b"accept-encoding"
            )

        resp = await call_next(request)

        if path not in DISABLE_COMPRESSION_PATHS:
            return resp

        # Force no compression
        resp.headers["Content-Encoding"] = "identity"
        resp.headers["X-Compression-Blocked"] = "1"
        resp.headers["Cache-Control"] = "no-store"

        # Jitter timing
        delay_ms = random.randint(PAD_MIN_MS, PAD_MAX_MS)
        await _sleep_ms(delay_ms)

        # Pad body
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
        return new_resp