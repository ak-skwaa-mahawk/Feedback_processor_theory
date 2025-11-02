=========================== api/service.py ===========================================

from future import annotations import os from typing import Any, Dict, Optional from fastapi import FastAPI, HTTPException, Request, Response from fastapi.responses import FileResponse, JSONResponse from pydantic import BaseModel

from synara_integration.flame_adapter import FlameAdapter from synara_integration.whisper_bridge import HandshakeGate from synara_integration.identity_sync import append_sacred_log, write_backup, seal_artifacts

--- Rate limiting (SlowAPI + Redis) ---

from slowapi import Limiter, _rate_limit_exceeded_handler from slowapi.util import get_remote_address from slowapi.errors import RateLimitExceeded from slowapi.middleware import SlowAPIMiddleware

REDIS_URL = os.getenv("WHISPER_REDIS_URL", "redis://localhost:6379/0") RATE_LIMIT = os.getenv("FPT_RATE_LIMIT", "10/minute")  # configurable

Prefer per-user key via receipt.key_id; fallback to client IP

async def key_func(request: Request) -> str: try: body = await request.json() rid = body.get("receipt", {}).get("key_id") if rid: return f"kid:{rid}" except Exception: pass return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=key_func, storage_uri=REDIS_URL)

app = FastAPI(title="Feedback Processor Theory — Synara Bridge", version="v1") app.state.limiter = limiter app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) app.add_middleware(SlowAPIMiddleware)

adapter = FlameAdapter() handshake = HandshakeGate()

class AnalyzeBody(BaseModel): conversation: str receipt: Dict[str, Any] expected_challenge: Optional[str] = None meta: Optional[Dict[str, Any]] = None

@app.get("/health") def health(): return {"ok": True, "service": app.title, "version": app.version}

@app.get("/limits") async def limits(request: Request): """Debug endpoint showing limiter configuration and computed key.""" try: computed_key = await key_func(request) except Exception: computed_key = f"ip:{get_remote_address(request)}" return { "rate_limit": RATE_LIMIT, "storage_uri": REDIS_URL, "computed_key": computed_key, }

@app.post("/fpt/analyze") @limiter.limit(RATE_LIMIT) async def analyze(request: Request, body: AnalyzeBody): ok, reason, ctx = handshake.verify(body.receipt, expected_challenge=body.expected_challenge) if not ok: raise HTTPException(status_code=401, detail=f"handshake_failed:{reason}")

# 1) compute metrics
metrics = adapter.analyze_resonance(body.conversation)

# 2) build sacred entry
entry = {
    "context": ctx,
    "meta": body.meta or {},
    "metrics": metrics,
}

# 3) persist (log + backup)
append_sacred_log(entry)
backup_path = write_backup(entry)

# 4) seal the result
seal = seal_artifacts("fpt_result", {**entry, "backup": str(backup_path)})

# 5) build response with rate-limit headers
headers = {}
state = request.state.limiter  # type: ignore
if hasattr(state, "current_limit"):
    headers = {
        "X-RateLimit-Limit": str(state.current_limit.limit if state.current_limit else RATE_LIMIT),
        "X-RateLimit-Remaining": str(state.remaining),
        "X-RateLimit-Reset": str(state.reset_time),
    }
data = {
    "status": "ok",
    "reason": reason,
    "context": ctx,
    "metrics": metrics,
    "backup": str(backup_path),
    "seal": seal,
}
return JSONResponse(content=data, headers=headers)

@app.get("/fpt/logs/latest") async def logs_latest(): from pathlib import Path from synara_integration.identity_sync import SACRED_LOG if not SACRED_LOG.exists(): raise HTTPException(status_code=404, detail="no_logs") import json data = json.loads(SACRED_LOG.read_text(encoding="utf-8")) if not data: raise HTTPException(status_code=404, detail="empty_logs") return {"latest": data[-1]}

@app.get("/fpt/qr.png") async def last_qr(): from pathlib import Path p = Path("data") pngs = sorted(p.glob("*.sigil.png"), reverse=True) if not pngs: raise HTTPException(status_code=404, detail="no_qr") return FileResponse(str(pngs[0]), media_type="image/png")

Run with: uvicorn api.service:app --host 0.0.0.0 --port 8081 --reload