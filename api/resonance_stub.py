from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
import hashlib, random

router = APIRouter(prefix="/resonance", tags=["resonance"])

class ScoreBody(BaseModel):
    digest: str
    requester: str
    context: dict | None = None

@router.post("/score")
def score(body: ScoreBody):
    # Pseudo-deterministic score (digest + requester salt); replace with your real model
    h = hashlib.sha256((body.digest + "|" + body.requester).encode()).hexdigest()
    rnd = int(h[:6], 16) / 0xFFFFFF
    # Optionally nudge score if context contains aligned keywords
    bump = 0.1 if any(k in (body.context or {}) for k in ("citation", "prior", "thesis")) else 0.0
    s = max(0.0, min(1.0, rnd * 0.9 + bump))
    return {"score": round(s, 3)}