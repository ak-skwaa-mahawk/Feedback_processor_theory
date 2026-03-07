from __future__ import annotations
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from modules.tunneling import (
    qm_T_rectangular, eV_to_J, M_ELECTRON,
    ftir_T, nm_to_m, deg_to_rad,
    arc_with_tunneling,
    waveguide_T_te10
)

from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser

router = APIRouter(tags=["Tunneling — Quantum Barrier Crossing"])

# ====================== SAHNEUTI-SEALED MODELS ======================
class QMRectRequest(BaseModel):
    mass_kg: float = Field(M_ELECTRON)
    barrier_height_eV: float = Field(..., gt=0)
    particle_energy_eV: float = Field(..., ge=0)
    barrier_width_nm: float = Field(..., gt=0)
    R_free: float = Field(0.0, ge=0.0)
    A: float = Field(0.0, ge=0.0)
    C: float = Field(0.15, ge=0.0)
    alpha: float = Field(1.0, ge=0.0)

class FTIRRequest(BaseModel):
    n1: float = Field(..., gt=0)
    n2: float = Field(..., gt=0)
    theta_deg: float = Field(..., ge=0, le=90)
    wavelength_nm: float = Field(..., gt=0)
    gap_nm: float = Field(..., gt=0)
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

class WaveguideRequest(BaseModel):
    n: float = Field(..., gt=0)
    a_mm: float = Field(..., gt=0)
    length_mm: float = Field(..., gt=0)
    wavelength_nm: float = Field(..., gt=0)
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

# ====================== ROUTES ======================
@router.post("/qm")
async def qm_tunneling(body: QMRectRequest, request: Request):
    V0 = eV_to_J(body.barrier_height_eV)
    E = eV_to_J(body.particle_energy_eV)
    d = body.barrier_width_nm * 1e-9
    T = 1.0 if E >= V0 else qm_T_rectangular(body.mass_kg, V0, E, d)
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)

    # Sovereign receipt + HUD trigger
    payload = {"T_qm": T, "arc": arc, "type": "qm_rect"}
    receipt = Handshake.createReceipt(request.app, "TUNNEL-QM", payload)
    if T >= 0.55:
        GlyphParser.parseAndProcess(f"TUNNEL-RESONANCE-{T:.3f}", None)

    return {"T_qm": T, "arc": arc, "sovereign_receipt": receipt}

@router.post("/ftir")
async def ftir_tunneling(body: FTIRRequest, request: Request):
    theta = deg_to_rad(body.theta_deg)
    lam = nm_to_m(body.wavelength_nm)
    gap = nm_to_m(body.gap_nm)
    T = ftir_T(body.n1, body.n2, theta, lam, gap)
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)

    payload = {"T_ftir": T, "arc": arc, "type": "ftir"}
    receipt = Handshake.createReceipt(request.app, "TUNNEL-FTIR", payload)
    if T >= 0.55:
        GlyphParser.parseAndProcess(f"TUNNEL-RESONANCE-{T:.3f}", None)

    return {"T_ftir": T, "arc": arc, "sovereign_receipt": receipt}

@router.post("/waveguide")
async def waveguide_tunneling(body: WaveguideRequest, request: Request):
    a_m = body.a_mm * 1e-3
    L_m = body.length_mm * 1e-3
    lam0_m = nm_to_m(body.wavelength_nm)
    T = waveguide_T_te10(body.n, a_m, lam0_m, L_m)
    lambda_c_nm = (2.0 * a_m) / body.n * 1e9
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)

    payload = {"T_wg": T, "arc": arc, "type": "waveguide"}
    receipt = Handshake.createReceipt(request.app, "TUNNEL-WAVEGUIDE", payload)
    if T >= 0.55:
        GlyphParser.parseAndProcess(f"TUNNEL-RESONANCE-{T:.3f}", None)

    return {"T_wg": T, "arc": arc, "lambda_c_nm": lambda_c_nm, "sovereign_receipt": receipt}