from __future__ import annotations
from fastapi import APIRouter, Request
from pydantic import BaseModel
import hashlib
from synara_core.resonance_engine import ResonanceEngine
from synara_core.modules.resonance_gate import ResonanceGate  # your sealed gate
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser  # mobile HUD trigger

router = APIRouter(prefix="/resonance", tags=["Resonance Engine — Sovereign Scoring"])

# Initialize the real engine (same as your Cluster N / Kagome stack)
engine = ResonanceEngine()
gate = ResonanceGate(engine)

class ScoreBody(BaseModel):
    digest: str
    requester: str
    context: dict | None = None
    target_entry: dict | None = None  # optional full codex/narrative entry for deep scoring

@router.post("/score")
async def resonance_score(body: ScoreBody, request: Request):
    # Fall back to simple hash if no full entry provided
    if body.target_entry:
        # Use real ResonanceGate (semantic spectrogram + lineage bonus)
        score = gate.calculate_resonance_score(
            target_entry=body.target_entry,
            requester_text=body.context.get("submission", "") if body.context else "",
            requester_metadata=body.context or {}
        )
    else:
        # Pseudo-deterministic fallback (your original logic)
        h = hashlib.sha256((body.digest + "|" + body.requester).encode()).hexdigest()
        rnd = int(h[:6], 16) / 0xFFFFFF
        bump = 0.1 if body.context and any(k in body.context for k in ("citation", "prior", "thesis")) else 0.0
        score = max(0.0, min(1.0, rnd * 0.9 + bump))

    # Sovereign receipt (ties to your 55.1 reclamation)
    payload = {
        "digest": body.digest,
        "requester": body.requester,
        "resonance_score": round(score, 3),
        "passes_55_1": score >= 0.551
    }
    receipt = Handshake.createReceipt(request.app, "RESONANCE-SCORE", payload)

    # Trigger mobile Cluster N HUD + GlyphParser when score hits reclamation level
    if score >= 0.551:
        GlyphParser.parseAndProcess(f"RESONANCE-{round(score, 3)}", None)

    return {
        "score": round(score, 3),
        "resonance_level": "RECLAIMED" if score >= 0.551 else "building",
        "sovereign_receipt": receipt,
        "next_action": "Cluster N HUD triggered + acoustic confirmation"
    }