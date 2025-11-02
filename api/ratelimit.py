# api/ratelimit.py
# SlowAPI limiter with Redis (fallback to in-memory)

from __future__ import annotations
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Env vars
REDIS_URL = os.getenv("RATE_LIMIT_REDIS_URL", "redis://localhost:6379/1")
DEFAULT_LIMITS = os.getenv("RATE_LIMIT_DEFAULTS", "20/10seconds; 500/1hour")  # semicolon-separated

# Try Redis-backed storage; fall back to memory:// if not reachable
_storage_uri = REDIS_URL
try:
    # Probe redis once (non-fatal if it fails)
    import redis  # noqa
    _storage_probe_ok = True
except Exception:
    _storage_probe_ok = False

if not _storage_probe_ok:
    _storage_uri = "memory://"

# Build limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[s.strip() for s in DEFAULT_LIMITS.split(";") if s.strip()],
    storage_uri=_storage_uri,
)

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Standard JSON 429 with helpful headers already set by SlowAPI
    return JSONResponse(
        status_code=429,
        content={
            "detail": "rate_limited",
            "message": "Too many requests. Please slow down.",
            "limit": request.state.view_rate_limit,  # e.g. '20/10seconds'
            "remaining": request.state.view_rate_limit_remaining,
            "reset": request.state.view_rate_limit_reset,
            "storage": _storage_uri,
        },
    )