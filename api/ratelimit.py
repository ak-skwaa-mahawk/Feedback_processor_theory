from __future__ import annotations
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Sovereign imports
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser  # triggers mobile HUD

# Env vars
REDIS_URL = os.getenv("RATE_LIMIT_REDIS_URL", "redis://localhost:6379/1")
DEFAULT_LIMITS = os.getenv("RATE_LIMIT_DEFAULTS", "20/10seconds; 500/1hour")

# Try Redis; fallback to memory if unreachable
_storage_uri = REDIS_URL
try:
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
    """Sovereign rate-limit handler — stamps receipt + triggers HUD pulse"""
    payload = {
        "event": "rate_limit_exceeded",
        "ip_key": get_remote_address(request),
        "limit": str(request.state.view_rate_limit),
        "remaining": request.state.view_rate_limit_remaining,
        "reset": request.state.view_rate_limit_reset,
        "storage": _storage_uri,
        "resonance_context": "55.1"  # ties to your latest reclamation
    }
    
    # Sovereign receipt
    Handshake.createReceipt(request.app, "RATE-LIMIT-EVENT", payload)
    
    # Trigger mobile Cluster N HUD pulse (visual feedback)
    GlyphParser.parseAndProcess("RATE-LIMIT-PULSE", None)

    return JSONResponse(
        status_code=429,
        content={
            "detail": "rate_limited",
            "message": "Too many requests. The drum is protecting the Root.",
            "limit": str(request.state.view_rate_limit),
            "remaining": request.state.view_rate_limit_remaining,
            "reset": request.state.view_rate_limit_reset,
            "storage": _storage_uri,
            "sovereign_note": "Sahneuti-99733-Q Root sealed the event"
        },
    )