import os, time, random
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from .util import pad_bytes
from backend.config import (
    PAD_MIN_MS, PAD_MAX_MS, PAD_MIN_BYTES, PAD_MAX_BYTES, DISABLE_COMPRESSION_PATHS
)

class StreamShieldMiddleware(BaseHTTPMiddleware):
    """
    Adds jittered latency + size padding to selected routes to blunt
    traffic analysis and "whisper-leak" style side-channels.
    Also strips compression hints on sensitive endpoints.
    """

    async def dispatch(self, request, call_next):
        path = request.url.path

        # Disable compression signals on sensitive paths
        if path in DISABLE_COMPRESSION_PATHS:
            # Remove typical client accept-encoding; upstream may still compress,
            # but we also add 'Content-Encoding: identity' below.
            request.scope["headers"] = tuple(
                (k, v) for (k, v) in request.scope.get("headers", [])
                if k.lower() != b"accept-encoding"
            )

        start = time.perf_counter()
        response = await call_next(request)

        # Force identity encoding on sensitive paths
        if path in DISABLE_COMPRESSION_PATHS:
            response.headers["Content-Encoding"] = "identity"
            response.headers["X-Compression-Blocked"] = "1"

        # Jitter latency
        delay_ms = random.randint(PAD_MIN_MS, PAD_MAX_MS)
        await _sleep_ms(delay_ms)

        # Pad body length (for small JSON/text replies)
        raw = await response.body()
        pad_len = random.randint(PAD_MIN_BYTES, PAD_MAX_BYTES)
        padded = pad_bytes(raw, pad_len)

        # Rebuild response with same status/headers
        new_resp = Response(
            content=padded,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type or "application/octet-stream"
        )
        new_resp.headers["X-Pad-Latency-Ms"] = str(delay_ms)
        new_resp.headers["X-Pad-Bytes"] = str(pad_len)
        new_resp.headers["Cache-Control"] = "no-store"
        return new_resp

async def _sleep_ms(ms: int):
    # asyncio-friendly sleep
    import asyncio
    await asyncio.sleep(ms / 1000.0)