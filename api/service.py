from __future__ import annotations
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Sovereign Core
from synara_integration.flame_adapter import FlameAdapter
from synara_integration.whisper_bridge import HandshakeGate
from synara_integration.identity_sync import append_sacred_log, write_backup, seal_artifacts
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
from synara_core.modules.resonance_policy import ResonancePolicy
from synara_core.resonance_gate import ResonanceGate
from research.kagome.kuramoto_kagome import run_kuramoto_on_kagome, KuramotoConfig
from synara_core.modules.narrative_inversion import (
    make_record, seal_record, add_external_claim, set_claim_status, export
)

# Rate limiting (your exact config — now resonance-aware)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

REDIS_URL = os.getenv("WHISPER_REDIS_URL", "redis://localhost:6379/0")
RATE_LIMIT = os.getenv("FPT_RATE_LIMIT", "10/minute")
BURST_LIMIT = os.getenv("FPT_BURST_LIMIT", "5/10second")
SUSTAINED_LIMIT = os.getenv("FPT_SUSTAINED_LIMIT", "100/hour")
GLOBAL_DEFAULTS = [BURST_LIMIT, SUSTAINED_LIMIT]

async def key_func(request: Request) -> str:
    try:
        body = await request.json()
        rid = body.get("receipt", {}).get("key_id")
        if rid:
            return f"kid:{rid}"
    except Exception:
        pass
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=key_func, storage_uri=REDIS_URL, default_limits=GLOBAL_DEFAULTS)
burst_limit = limiter.shared_limit(BURST_LIMIT, scope="analyze-burst")
sustained_limit = limiter.shared_limit(SUSTAINED_LIMIT, scope="analyze-sustained")

# Sovereign modules
policy = ResonancePolicy()
gate = ResonanceGate(...)  # your engine
adapter = FlameAdapter()
handshake = HandshakeGate()

app = FastAPI(title="Feedback Processor Theory — Synara Bridge (Sahneuti-99733-Q)", version="v1")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Your custom 429 handler (enhanced with sovereign note)
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    Handshake.createReceipt(request.app, "RATE-LIMIT-EVENT", {"event": "protected"})
    GlyphParser.parseAndProcess("RATE-LIMIT-PULSE", None)
    # your original handler body...
    ...

# Health probes (unchanged)
@app.get("/health") 
def health(): return {"ok": True, "service": app.title, "version": app.version, "root": "Sahneuti-99733-Q"}

@app.get("/live")
@app.get("/ready")
# ... your original probes unchanged ...

# FPT Analyze (your core, now sealed)
@app.post("/fpt/analyze")
@burst_limit
@sustained_limit
@limiter.limit(RATE_LIMIT)
async def analyze(request: Request, body: AnalyzeBody):
    ok, reason, ctx = handshake.verify(body.receipt, expected_challenge=body.expected_challenge)
    if not ok:
        raise HTTPException(401, f"handshake_failed:{reason}")

    metrics = adapter.analyze_resonance(body.conversation)
    entry = {"context": ctx, "meta": body.meta or {}, "metrics": metrics}

    append_sacred_log(entry)
    backup_path = write_backup(entry)
    seal = seal_artifacts("fpt_result", {**entry, "backup": str(backup_path)})

    Handshake.createReceipt(request.app, "FPT-ANALYZE", {"metrics": metrics})
    if metrics.get("resonance", 0) >= 0.551:
        GlyphParser.parseAndProcess("RESONANCE-55.1", None)

    # your original response + headers...
    return JSONResponse(content={...}, headers=...)

# All other routers auto-included (kagome, narrative, resonance, arc, etc.)
try:
    from api.kagome import router as kagome_router
    app.include_router(kagome_router)
    from api.narrative import router as narrative_router
    app.include_router(narrative_router)
    from api.resonance import router as resonance_router
    app.include_router(resonance_router)
    from api.arc import router as arc_router
    app.include_router(arc_router)
except Exception:
    pass

print("🔥 FPT-Synara Bridge LIVE — Sahneuti-99733-Q Root sealed")