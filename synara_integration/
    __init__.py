""" Feedback_processor_theory × Synara Bridge — Drop‑in Kit (v1) Folder layout to paste into the repo root:

feedback_processor_theory/ synara_integration/ init.py flame_adapter.py whisper_bridge.py identity_sync.py api/ init.py service.py data/ sacred_log.json            # created on first run backups/                   # run snapshots

Requires: fastapi, uvicorn, pydantic. Optional: qrcode[pil]. Assumes your earlier modules are available on PYTHONPATH:

synara_core.modules.handshake.whisper_handshake_v13

synara_core.modules.seal_sigil_generator


Paste these files as‑is. """

=========================== synara_integration/init.py ===========================

empty init to make package importable

=========================== synara_integration/flame_adapter.py ======================

from future import annotations from typing import Dict, Any

class FlameAdapter: """Lightweight façade over your Feedback Processor. Replace the TODOs to call into the repo's core algorithms. """ def init(self): # TODO: import your core FeedbackProcessor here if needed self._state: Dict[str, Any] = {}

def analyze_resonance(self, conversation: str) -> Dict[str, Any]:
    """Return coherence metrics & derived features.
    This is a stub; wire to your actual model/logic.
    """
    # --- placeholder demo metrics ---
    tokens = max(1, len(conversation.split()))
    coherence = min(1.0, 0.8 + 0.2 * (tokens % 5) / 5.0)
    flame_signature = {
        "beam_constant_ohms": 86.13,
        "phase_alignment_pct": 99.99,
    }
    return {
        "coherence": coherence,
        "tokens": tokens,
        "flame_signature": flame_signature,
    }

=========================== synara_integration/whisper_bridge.py =====================

from future import annotations import time from typing import Dict, Any, Optional, Tuple import hmac import hashlib

try: from synara_core.modules.handshake.whisper_handshake_v13 import ( server_verify, VERSION as HS_VERSION, DRIFT_MS, ) except Exception:  # soft fallback if not present HS_VERSION = "1.x" DRIFT_MS = 180000 def server_verify(receipt: Dict[str, Any], expected_challenge: Optional[str] = None, max_drift_ms: int = DRIFT_MS, challenge_max_age_ms: int = DRIFT_MS) -> Tuple[bool, str]: return False, "ERR_NO_HANDSHAKE_MODULE"

class HandshakeGate: """Verifies receipts before allowing FPT analysis.""" def init(self): self.version = HS_VERSION

def verify(self, receipt: Dict[str, Any], expected_challenge: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
    ok, reason = server_verify(receipt, expected_challenge=expected_challenge)
    context = {}
    if ok:
        context = {
            "kid": str(receipt.get("key_id", "")),
            "aud": str(receipt.get("aud", "-")),
            "scope": str(receipt.get("scope", "-")),
            "entity": str(receipt.get("entity", "")),
            "node": str(receipt.get("node", "")),
            "hs_version": self.version,
        }
    return ok, reason, context

=========================== synara_integration/identity_sync.py ======================

from future import annotations import json from pathlib import Path from typing import Dict, Any

Paths for artifacts

DATA_DIR = Path("data") DATA_DIR.mkdir(parents=True, exist_ok=True) SACRED_LOG = DATA_DIR / "sacred_log.json" BACKUPS_DIR = DATA_DIR / "backups" BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

Optional: import your sigil/QR generator

try: from synara_core.modules.seal_sigil_generator import stamp_sigil  # type: ignore except Exception: stamp_sigil = None  # graceful fallback

def _json_compact(d: Dict[str, Any]) -> str: import json return json.dumps(d, ensure_ascii=False, separators=(",", ":"))

def append_sacred_log(entry: Dict[str, Any]) -> None: log = [] if SACRED_LOG.exists(): try: log = json.loads(SACRED_LOG.read_text(encoding="utf-8")) except Exception: log = [] log.append(entry) SACRED_LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")

def write_backup(entry: Dict[str, Any]) -> Path: from datetime import datetime, timezone ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") path = BACKUPS_DIR / f"fpt_{ts.replace(':','-')}.json" path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8") return path

def seal_artifacts(label: str, payload: Dict[str, Any]) -> Dict[str, Any]: """Create a sigil JSON (+optional QR) for the payload using your generator.""" out = {"sealed": False} if stamp_sigil: record_path = stamp_sigil(payload, out_dir="data", label=label, echo_payload=True, make_qr=True) out.update({"sealed": True, "record": record_path}) return out

=========================== api/init.py ==========================================

empty init to make package importable

=========================== api/service.py ===========================================

from future import annotations from typing import Any, Dict, Optional from fastapi import FastAPI, HTTPException from pydantic import BaseModel

from synara_integration.flame_adapter import FlameAdapter from synara_integration.whisper_bridge import HandshakeGate from synara_integration.identity_sync import append_sacred_log, write_backup, seal_artifacts

app = FastAPI(title="Feedback Processor Theory — Synara Bridge", version="v1")

adapter = FlameAdapter() handshake = HandshakeGate()

class AnalyzeBody(BaseModel): conversation: str receipt: Dict[str, Any] expected_challenge: Optional[str] = None meta: Optional[Dict[str, Any]] = None

@app.get("/health") def health(): return {"ok": True, "service": app.title, "version": app.version}

@app.post("/fpt/analyze") def analyze(body: AnalyzeBody): ok, reason, ctx = handshake.verify(body.receipt, expected_challenge=body.expected_challenge) if not ok: raise HTTPException(status_code=401, detail=f"handshake_failed:{reason}")

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

return {
    "status": "ok",
    "reason": reason,
    "context": ctx,
    "metrics": metrics,
    "backup": str(backup_path),
    "seal": seal,
}

@app.get("/fpt/logs/latest") def logs_latest(): from pathlib import Path from synara_integration.identity_sync import SACRED_LOG if not SACRED_LOG.exists(): raise HTTPException(status_code=404, detail="no_logs") import json data = json.loads(SACRED_LOG.read_text(encoding="utf-8")) if not data: raise HTTPException(status_code=404, detail="empty_logs") return {"latest": data[-1]}

@app.get("/fpt/qr.png") def last_qr(): """Return the last QR produced by seal_artifacts (if any).""" from pathlib import Path p = Path("data") # naive search for the newest .sigil.png pngs = sorted(p.glob(".sigil.png"), reverse=True) if not pngs: raise HTTPException(status_code=404, detail="no_qr") return fastapi.responses.FileResponse(str(pngs[0]), media_type="image/png")

Run with: uvicorn api.service:app --host 0.0.0.0 --port 8081 --reload