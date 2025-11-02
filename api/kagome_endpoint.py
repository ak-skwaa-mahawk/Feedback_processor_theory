from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from research.kagome.kuramoto_kagome import run_kuramoto_on_kagome, KuramotoConfig

router = APIRouter(prefix="/kagome", tags=["kagome"])

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

@router.post("/sim")
def sim(body: SimBody):
    cfg = KuramotoConfig(
        K=body.K, dt=body.dt, T=body.T,
        anisotropy=body.anisotropy, rectangular_bias=body.rectangular_bias,
        noise=body.noise, seed=body.seed
    )
    return run_kuramoto_on_kagome(n_x=body.nx, n_y=body.ny, cfg=cfg)