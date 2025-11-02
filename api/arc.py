from slowapi import Limiter
from fastapi import APIRouter, HTTPException, Query
from api.ratelimit import limiter  # NEW

router = APIRouter(tags=["ARC"])

@router.get("/eval")
@limiter.limit("30/minute")          # per-IP
@limiter.limit("6/10seconds")        # short burst control
def arc_eval(...):
    ...

@router.post("/sweep")
@limiter.limit("10/minute")          # heavier endpoint
@limiter.limit("3/10seconds")
def arc_sweep(body: ArcSweepRequest):
    ...

@router.get("/presets")
@limiter.limit("60/minute")
def arc_presets():
    ...
# api/arc.py
# FastAPI router for Attenuation–Return Criterion (ARC) evaluation
# Depends on modules/sound_resonance.py

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from modules.sound_resonance import (
    simulate_path, sweep_frequencies, AIR, HELIO, VAC
)

router = APIRouter(tags=["ARC"])

# ---- Schemas ----

class ArcEvalResponse(BaseModel):
    medium: str
    distance_m: float
    frequency_hz: float
    attenuation: float
    return_: float = Field(alias="return")
    arc: float
    passes: bool
    rgb: List[int]
    audible_0_1: float

class ArcSweepRequest(BaseModel):
    distance_m: float = Field(..., gt=0, description="Propagation distance in meters")
    frequencies_hz: List[float] = Field(..., min_items=1, description="List of frequencies to sample")
    medium: str = Field("air", description="one of: air, helio, vac")
    threshold: float = Field(0.15, ge=0.0, description="ARC threshold C")

class ArcSweepResponse(BaseModel):
    results: List[ArcEvalResponse]

# ---- helpers ----

_MEDIUMS = {
    "air": AIR,
    "helio": HELIO,
    "vac": VAC,
    "interstellar": VAC,
    "heliosphere": HELIO,
    "atmosphere": AIR,
}

def _get_medium(name: str):
    key = (name or "").strip().lower()
    if key not in _MEDIUMS:
        raise HTTPException(status_code=400, detail=f"unknown medium '{name}', choose one of: {', '.join(sorted(_MEDIUMS))}")
    return _MEDIUMS[key]

# ---- routes ----

@router.get("/eval", response_model=ArcEvalResponse)
def arc_eval(
    distance_m: float = Query(..., gt=0, description="Propagation distance in meters"),
    frequency_hz: float = Query(..., gt=0, description="Signal frequency in Hz"),
    medium: str = Query("air", description="air | helio | vac"),
    threshold: float = Query(0.15, ge=0.0, description="ARC threshold C"),
):
    m = _get_medium(medium)
    res = simulate_path(distance_m, frequency_hz, m, C=threshold)
    # pydantic expects key 'return', FastAPI reserves 'return', so keep alias
    res["return"] = res.pop("return")
    return res

@router.post("/sweep", response_model=ArcSweepResponse)
def arc_sweep(body: ArcSweepRequest):
    m = _get_medium(body.medium)
    results = sweep_frequencies(body.distance_m, body.frequencies_hz, medium=m, C=body.threshold)
    # rename 'return' keys for model alias
    for r in results:
        r["return"] = r.pop("return")
    return {"results": results}

@router.get("/presets")
def arc_presets():
    return {
        "media": list(sorted(_MEDIUMS.keys())),
        "examples": {
            "audio_3k_air_10m": {"distance_m": 10.0, "frequency_hz": 3_000.0, "medium": "air"},
            "visible_green_air_10m": {"distance_m": 10.0, "frequency_hz": 5.5e14, "medium": "air"},
            "uv_vac_1e9m": {"distance_m": 1.0e9, "frequency_hz": 9.0e14, "medium": "vac"},
        },
        "threshold_default": 0.15
    }