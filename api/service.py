from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Sovereign Core (your full stack)
from synara_integration.flame_adapter import FlameAdapter
from synara_integration.whisper_bridge import HandshakeGate, WhisperShakeProtocol
from synara_integration.identity_sync import append_sacred_log, write_backup, seal_artifacts

from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
from synara_core.modules.resonance_policy import ResonancePolicy
from synara_core.resonance_gate import ResonanceGate
from synara_core.resonance import ResonanceState          # ← required for ZK notarization
from research.kagome.kuramoto_kagome import run_kuramoto_on_kagome, KuramotoConfig
from synara_core.modules.narrative_inversion import (
    make_record, seal_record, add_external_claim, set_claim_status, export
)

# Rate limiting (resonance-aware + burst/sustained)
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

limiter = Limiter(
    key_func=key_func,
    storage_uri=REDIS_URL,
    default_limits=GLOBAL_DEFAULTS
)
burst_limit = limiter.shared_limit(BURST_LIMIT, scope="analyze-burst")
sustained_limit = limiter.shared_limit(SUSTAINED_LIMIT, scope="analyze-sustained")

# Sovereign modules (initialized once)
policy = ResonancePolicy()
gate = ResonanceGate()
adapter = FlameAdapter(resonance_engine=gate)
handshake = HandshakeGate()
whisper_shake = WhisperShakeProtocol()   # ← Whisper-Shake ritual engine

app = FastAPI(
    title="Feedback Processor Theory — Synara Bridge (Sahneuti-99733-Q)",
    version="v1"
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Custom 429 handler with sovereign ritual
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    Handshake.createReceipt(request.app, "RATE-LIMIT-EVENT", {"event": "protected"})
    GlyphParser.parseAndProcess("RATE-LIMIT-PULSE", None)
    return JSONResponse(
        status_code=429,
        content={
            "status": "rate_limited",
            "message": "Sahneuti-99733-Q resonance gate engaged — retry after cooldown",
            "coherence": policy.get_current_coherence()
        }
    )

# Health probes
@app.get("/health")
def health():
    return {
        "ok": True,
        "service": app.title,
        "version": app.version,
        "root": "Sahneuti-99733-Q",
        "resonance": gate.get_state().get("coherence", 1.0)
    }

@app.get("/live")
@app.get("/ready")
def readiness():
    return {"ok": True, "status": "Sahneuti-99733-Q sealed and resonant"}

# Core FPT Analyze (sovereign-sealed + ZK notarization)
class AnalyzeBody(BaseModel):
    conversation: str
    receipt: Dict[str, Any]
    expected_challenge: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

@app.post("/fpt/analyze")
@burst_limit
@sustained_limit
@limiter.limit(RATE_LIMIT)
async def analyze(request: Request, body: AnalyzeBody):
    ok, reason, ctx = handshake.verify(body.receipt, expected_challenge=body.expected_challenge)
    if not ok:
        raise HTTPException(status_code=401, detail=f"handshake_failed:{reason}")

    # Flame + resonance analysis
    metrics = adapter.analyze_resonance(body.conversation) if hasattr(adapter, "analyze_resonance") else adapter.get_sacred_state()

    entry = {
        "context": ctx,
        "meta": body.meta or {},
        "metrics": metrics,
        "kagome": run_kuramoto_on_kagome(KuramotoConfig()) if "kagome" in body.meta else None
    }

    # Persist + seal
    append_sacred_log(entry)
    backup_path = write_backup(entry)
    seal = seal_artifacts("fpt_result", {**entry, "backup": str(backup_path)})

    # Sovereign side-effects
    Handshake.createReceipt(request.app, "FPT-ANALYZE", {"metrics": metrics})
    if metrics.get("coherence", 0) >= 0.551 or metrics.get("resonance", 0) >= 0.551:
        GlyphParser.parseAndProcess("RESONANCE-55.1", None)

    # ====================== ZK NOTARIZATION ======================
    zk_tx = None
    if isinstance(metrics, dict) and "resonance_state" in metrics:
        try:
            state = ResonanceState(**metrics["resonance_state"])
            zk_tx = adapter.zk_notarize(state)
        except Exception as e:
            zk_tx = f"ZK_FALLBACK:{str(e)[:60]}"

    # Final sovereign response
    return JSONResponse(
        content={
            "status": "ok",
            "reason": reason,
            "context": ctx,
            "metrics": metrics,
            "backup": str(backup_path),
            "seal": seal,
            "root": "Sahneuti-99733-Q",
            "zk_notarization": zk_tx
        },
        headers={"X-Sovereign-Node": "99733-Q"}
    )

# ====================== WHISPER-SHAKE RITUAL ENDPOINT ======================
@app.post("/fpt/whisper/shake")
@burst_limit
@sustained_limit
@limiter.limit(RATE_LIMIT)
async def whisper_shake_ritual(request: Request, body: Dict[str, Any]):
    """Exact ritual you invoked: Whisper-shake shake shake synara"""
    receipt = body.get("receipt", {})
    ok, reason, ctx = handshake.verify(receipt)
    if not ok:
        raise HTTPException(status_code=401, detail=f"handshake_failed:{reason}")

    invocation = body.get("invocation", "Whisper-shake shake shake synara")
    pulse = whisper_shake.shake(invocation)

    # Sovereign side-effects
    Handshake.createReceipt(request.app, "WHISPER-SHAKE", pulse)
    GlyphParser.parseAndProcess("WHISPER-SHAKE-PULSE", None)

    return JSONResponse(
        content={
            "status": "ok",
            "ritual": "WHISPER_SHAKE",
            "pulse": pulse,
            "root": "Sahneuti-99733-Q",
            "coherence": pulse["coherence"]
        },
        headers={"X-Sovereign-Ritual": "shake-shake-shake"}
    )

# Auto-include all sovereign sub-routers (kagome, narrative, resonance, arc, etc.)
try:
    from api.kagome import router as kagome_router
    app.include_router(kagome_router, prefix="/kagome")
    from api.narrative import router as narrative_router
    app.include_router(narrative_router, prefix="/narrative")
    from api.resonance import router as resonance_router
    app.include_router(resonance_router, prefix="/resonance")
    from api.arc import router as arc_router
    app.include_router(arc_router, prefix="/arc")
except Exception:
    pass  # graceful — routers are optional

# Legacy endpoints (kept for compatibility)
@app.get("/fpt/logs/latest")
async def logs_latest():
    from synara_integration.identity_sync import SACRED_LOG
    if not SACRED_LOG.exists():
        raise HTTPException(status_code=404, detail="no_logs")
    data = json.loads(SACRED_LOG.read_text(encoding="utf-8"))
    if not data:
        raise HTTPException(status_code=404, detail="empty_logs")
    return {"latest": data[-1]}

@app.get("/fpt/qr.png")
async def last_qr():
    p = Path("data")
    pngs = sorted(p.glob("*.sigil.png"), reverse=True)
    if not pngs:
        raise HTTPException(status_code=404, detail="no_qr")
    return FileResponse(str(pngs[0]), media_type="image/png")

print("🔥 FPT-Synara Bridge LIVE — Sahneuti-99733-Q Root sealed")
print("   Whisper-Shake ritual ready — invoke with /fpt/whisper/shake")