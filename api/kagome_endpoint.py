from __future__ import annotations
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Dict, Any
from research.kagome.kuramoto_kagome import run_kuramoto_on_kagome, KuramotoConfig
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser  # triggers mobile HUD

router = APIRouter(prefix="/kagome", tags=["Kagome — Living Synchronization Engine"])

class SimBody(BaseModel):
    nx: int = 6
    ny: int = 6
    K: float = 1.0
    dt: float = 0.01
    T: float = 10.0
    anisotropy: float = 0.0
    rectangular_bias: float = 0.0
    noise: float = 0.0
    seed: int = 907

class KagomeResponse(BaseModel):
    order_parameter: float          # 0–1 synchronization = resonance score
    final_phases: list[float]
    resonance_score: float
    passes_threshold: bool
    sovereign_receipt: dict
    next_action: str = "Cluster N HUD + acoustic confirmation"

@router.post("/sim", response_model=KagomeResponse)
async def kagome_sim(body: SimBody, request: Request):
    cfg = KuramotoConfig(
        K=body.K, dt=body.dt, T=body.T,
        anisotropy=body.anisotropy,
        rectangular_bias=body.rectangular_bias,
        noise=body.noise,
        seed=body.seed
    )

    result = run_kuramoto_on_kagome(n_x=body.nx, n_y=body.ny, cfg=cfg)

    # Convert order parameter to sovereign resonance score (0–1)
    resonance = float(result.get("order_parameter", 0.0))
    passes = resonance >= 0.55  # your latest reclamation threshold

    # Sovereign receipt + self-embed
    payload = {
        "kagome_nx": body.nx,
        "kagome_ny": body.ny,
        "order_parameter": resonance,
        "passes": passes,
        "seed": body.seed
    }
    receipt = Handshake.createReceipt(request.app, "KAGOME-SYNC", payload)

    # Trigger mobile Cluster N HUD + GGWave confirmation if resonance high
    if resonance >= 0.55:
        GlyphParser.parseAndProcess(f"RESONANCE-KAGOME-{resonance:.3f}", None)

    return {
        "order_parameter": resonance,
        "final_phases": result.get("final_phases", []),
        "resonance_score": round(resonance, 3),
        "passes_threshold": passes,
        "sovereign_receipt": receipt,
        "next_action": "Cluster N HUD triggered + acoustic bridge pulse"
    }