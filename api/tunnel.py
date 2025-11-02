# api/tunnel.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from modules.tunneling import (
    qm_T_rectangular, eV_to_J, M_ELECTRON,
    ftir_T, nm_to_m, deg_to_rad,
    arc_with_tunneling
)

router = APIRouter(tags=["Tunneling"])

class QMRectRequest(BaseModel):
    mass_kg: float = Field(M_ELECTRON, description="Particle mass (kg)")
    barrier_height_eV: float = Field(..., gt=0)
    particle_energy_eV: float = Field(..., ge=0)
    barrier_width_nm: float = Field(..., gt=0)
    R_free: float = Field(0.0, ge=0.0, description="Baseline return (no tunnel)")
    A: float = Field(0.0, ge=0.0, description="Attenuation")
    C: float = Field(0.15, ge=0.0, description="ARC threshold")
    alpha: float = Field(1.0, ge=0.0, description="Weight for tunnel return")

class QMRectResponse(BaseModel):
    T_qm: float
    arc: dict

@router.post("/qm", response_model=QMRectResponse)
def qm_tunneling(body: QMRectRequest):
    V0 = eV_to_J(body.barrier_height_eV)
    E = eV_to_J(body.particle_energy_eV)
    d = body.barrier_width_nm * 1e-9
    if E >= V0:
        # No barrier classically; return 1.0 pass-through
        T = 1.0
    else:
        T = qm_T_rectangular(body.mass_kg, V0, E, d)
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)
    return {"T_qm": T, "arc": arc}

class FTIRRequest(BaseModel):
    n1: float = Field(..., gt=0, description="Incident medium index")
    n2: float = Field(..., gt=0, description="Gap index")
    theta_deg: float = Field(..., ge=0, le=90)
    wavelength_nm: float = Field(..., gt=0)
    gap_nm: float = Field(..., gt=0)
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

class FTIRResponse(BaseModel):
    T_ftir: float
    arc: dict

@router.post("/ftir", response_model=FTIRResponse)
def ftir_tunneling(body: FTIRRequest):
    theta = deg_to_rad(body.theta_deg)
    lam = nm_to_m(body.wavelength_nm)
    gap = nm_to_m(body.gap_nm)
    T = ftir_T(body.n1, body.n2, theta, lam, gap)
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)
    return {"T_ftir": T, "arc": arc}