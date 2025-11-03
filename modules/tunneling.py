from modules.tunneling import (
    # existing imports ...
    metal_T_skin_depth, waveguide_T_te10, nm_to_m
)
# --- Metal film (skin-depth tunneling) -----------------------------------------
# Ohmic conductor model (RF / microwave friendly). For optics you’d normally use
# complex ε(ω); here we use the classic skin-depth δ = sqrt(2/(μ σ ω)).
# Transmission magnitude across thickness t: T ≈ exp(-2 t / δ)

def metal_T_skin_depth(
    sigma_S_per_m: float,        # conductivity, e.g. Cu ~ 5.8e7 S/m
    freq_Hz: float,              # frequency
    thickness_m: float,          # metal thickness
    mu_r: float = 1.0            # relative permeability (≈1 for Cu/Al)
) -> float:
    if sigma_S_per_m <= 0 or freq_Hz <= 0 or thickness_m < 0:
        return 0.0
    omega = 2.0 * math.pi * freq_Hz
    delta = skin_depth(omega=omega, sigma=sigma_S_per_m, mu_r=mu_r)
    return math.exp(-2.0 * thickness_m / delta)class MetalRequest(BaseModel):
    sigma_S_per_m: float = Field(..., gt=0, description="Conductivity (S/m), e.g. Cu~5.8e7")
    freq_Hz: float = Field(..., gt=0, description="Frequency (Hz)")
    thickness_um: float = Field(..., ge=0, description="Metal thickness (μm)")
    mu_r: float = Field(1.0, gt=0, description="Relative permeability (≈1)")
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

class MetalResponse(BaseModel):
    T_metal: float
    arc: dict
    skin_depth_um: float

@router.post("/metal", response_model=MetalResponse)
def metal_tunneling(body: MetalRequest):
    t_m = body.thickness_um * 1e-6
    T = metal_T_skin_depth(body.sigma_S_per_m, body.freq_Hz, t_m, mu_r=body.mu_r)

    # compute skin depth for reference
    omega = 2.0 * math.pi * body.freq_Hz
    delta_m = skin_depth(omega=omega, sigma=body.sigma_S_per_m, mu_r=body.mu_r)

    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)
    return {"T_metal": T, "arc": arc, "skin_depth_um": delta_m * 1e6}
# modules/tunneling.py
# Quantum + Electromagnetic tunneling utilities for ARC integration

from __future__ import annotations
import math
from typing import Dict

HBAR = 1.054_571_817e-34  # J*s
E_CHARGE = 1.602_176_634e-19  # C
M_ELECTRON = 9.109_383_7015e-31  # kg
MU0 = 4*math.pi*1e-7  # H/m

def qm_kappa(m_kg: float, V0_J: float, E_J: float) -> float:
    """Decay constant inside barrier (quantum), κ = sqrt(2m(V0 - E))/ħ for E < V0."""
    if E_J >= V0_J:
        return 0.0
    return math.sqrt(2.0 * m_kg * (V0_J - E_J)) / HBAR

def qm_T_rectangular(m_kg: float, V0_J: float, E_J: float, d_m: float) -> float:
    """
    Approx tunneling probability through a rectangular barrier.
    Returns exp(-2 κ d). Caller can apply prefactors if needed.
    """
    kappa = qm_kappa(m_kg, V0_J, E_J)
    return math.exp(-2.0 * kappa * d_m)

def ftir_kappa(n1: float, n2: float, theta_rad: float, wavelength_m: float) -> float:
    """
    Evanescent decay κ for FTIR (n1 > n2, theta above critical).
    κ = k0 * sqrt(n1^2 sin^2 θ - n2^2), k0 = 2π/λ
    """
    k0 = 2.0 * math.pi / wavelength_m
    term = n1**2 * (math.sin(theta_rad)**2) - n2**2
    return 0.0 if term <= 0 else k0 * math.sqrt(term)

def ftir_T(n1: float, n2: float, theta_rad: float, wavelength_m: float, gap_m: float) -> float:
    """
    Approx evanescent tunneling across a low-index gap of thickness d (FTIR).
    Returns exp(-2 κ d). Fresnel coupling factors can be added externally.
    """
    kappa = ftir_kappa(n1, n2, theta_rad, wavelength_m)
    return math.exp(-2.0 * kappa * gap_m) if kappa > 0 else 0.0

def skin_depth(omega: float, sigma: float, mu_r: float = 1.0) -> float:
    """
    Skin depth in a conductor: δ = sqrt(2 / (μ σ ω)), μ = μ0 μr
    """
    mu = MU0 * mu_r
    return math.sqrt(2.0 / (mu * sigma * omega))

def arc_with_tunneling(R_free: float, A: float, C: float, T_tun: float, alpha: float = 1.0) -> Dict:
    """
    Blend tunneling return into ARC decision:
      R' = R_free + alpha * T_tun
      passes = (R' - A) >= C
    """
    R_prime = R_free + alpha * T_tun
    return {
        "R_free": R_free,
        "T_tun": T_tun,
        "alpha": alpha,
        "R_prime": R_prime,
        "A": A,
        "C": C,
        "passes": (R_prime - A) >= C
    }

# Convenience helpers for common units
def eV_to_J(eV: float) -> float:
    return eV * E_CHARGE

def nm_to_m(nm: float) -> float:
    return nm * 1e-9

def deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0
# --- Waveguide-below-cutoff (TE10, rectangular) --------------------------------
# Assumptions: non-magnetic filling (μ_r ≈ 1), refractive index n, dominant TE10,
# broad wall dimension = a, height b large (ignore higher-order terms).
# Cutoff: λ_c ≈ 2a / n. For λ0 > λ_c (i.e., n*λ0 > 2a), propagation constant becomes imaginary.
# Attenuation constant α_wg = sqrt( (π/a)^2 - (n*2π/λ0)^2 ), giving evanescent decay e^{-α L}.

def waveguide_alpha_te10(n: float, a_m: float, lambda0_m: float) -> float:
    """Evanescent attenuation constant α for TE10 below cutoff."""
    if n <= 0 or a_m <= 0 or lambda0_m <= 0:
        return 0.0
    k_c = math.pi / a_m                 # cutoff wavenumber term (TE10)
    k0 = 2.0 * math.pi / lambda0_m      # free-space wavenumber
    k = n * k0
    term = (k_c**2) - (k**2)
    return math.sqrt(term) if term > 0 else 0.0

def waveguide_T_te10(n: float, a_m: float, lambda0_m: float, length_m: float) -> float:
    """
    Transmission magnitude through below-cutoff section of length L (dominant TE10):
      T ≈ exp(-2 α L), matching the same e^{-2 κ d} convention used elsewhere.
    """
    alpha = waveguide_alpha_te10(n, a_m, lambda0_m)
    return math.exp(-2.0 * alpha * length_m) if alpha > 0 else (1.0 if n*lambda0_m <= 2*a_m else 0.0)
# modules/tunneling.py
import math

# --- If you already have these helpers, keep yours ----------------------------
# Placeholders below for context. Keep your existing versions if present.
M_ELECTRON = 9.10938356e-31
HBAR = 1.054571817e-34
MU0 = 4e-7 * math.pi

def eV_to_J(ev: float) -> float:
    return ev * 1.602176634e-19

def nm_to_m(nm: float) -> float:
    return nm * 1e-9

def deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0

def skin_depth(omega: float, sigma: float, mu_r: float = 1.0) -> float:
    mu = MU0 * mu_r
    return math.sqrt(2.0 / (mu * sigma * omega))

def qm_T_rectangular(m_kg: float, V0_J: float, E_J: float, d_m: float) -> float:
    # T ~ exp(-2 κ d), κ = sqrt(2m(V0 - E))/ħ   for E<V0
    if E_J >= V0_J: 
        return 1.0
    kappa = math.sqrt(2.0 * m_kg * (V0_J - E_J)) / HBAR
    return math.exp(-2.0 * kappa * d_m)

def ftir_T(n1: float, n2: float, theta_rad: float, lambda_m: float, gap_m: float) -> float:
    # Evanescent FTIR approximation: T ~ exp(-2 κ d), κ = k0 sqrt(n1^2 sin^2θ - n2^2)
    k0 = 2.0 * math.pi / lambda_m
    s = (n1 * math.sin(theta_rad))**2 - (n2**2)
    if s <= 0:
        return 0.0
    kappa = k0 * math.sqrt(s)
    return math.exp(-2.0 * kappa * gap_m)

# --- ARC combiner (keep your existing if present) -----------------------------
def arc_with_tunneling(R_free: float, A: float, C: float, T_tun: float, alpha: float = 1.0):
    Rprime = R_free + alpha * T_tun
    return {
        "R_prime": Rprime,
        "passes": (Rprime - A) >= C,
        "A": A, "C": C, "alpha": alpha, "T": T_tun,
    }

# --- Waveguide-below-cutoff (TE10) --------------------------------------------
def waveguide_alpha_te10(n: float, a_m: float, lambda0_m: float) -> float:
    """ Evanescent attenuation constant α for TE10 below cutoff (air/weakly magnetic). """
    if n <= 0 or a_m <= 0 or lambda0_m <= 0:
        return 0.0
    k_c = math.pi / a_m                 # TE10 cutoff term
    k0 = 2.0 * math.pi / lambda0_m      # free-space wavenumber
    k = n * k0
    term = (k_c**2) - (k**2)
    return math.sqrt(term) if term > 0 else 0.0

def waveguide_T_te10(n: float, a_m: float, lambda0_m: float, length_m: float) -> float:
    """
    Transmission magnitude through below-cutoff section length L (TE10):
    T ≈ exp(-2 α L); if not below cutoff, revert to 1.0.
    """
    alpha = waveguide_alpha_te10(n, a_m, lambda0_m)
    return math.exp(-2.0 * alpha * length_m) if alpha > 0 else 1.0

# --- Metal film (skin-depth) --------------------------------------------------
def metal_T_skin_depth(
    sigma_S_per_m: float,        # e.g., Cu ~ 5.8e7 S/m
    freq_Hz: float,              # frequency
    thickness_m: float,          # metal thickness
    mu_r: float = 1.0            # ≈1 for Cu/Al; >1 for ferromagnetics
) -> float:
    if sigma_S_per_m <= 0 or freq_Hz <= 0 or thickness_m < 0:
        return 0.0
    omega = 2.0 * math.pi * freq_Hz
    delta = skin_depth(omega=omega, sigma=sigma_S_per_m, mu_r=mu_r)
    return math.exp(-2.0 * thickness_m / delta)
# api/tunnel.py
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from io import BytesIO
import math
import matplotlib.pyplot as plt

from modules.tunneling import (
    M_ELECTRON, eV_to_J, nm_to_m, deg_to_rad,
    qm_T_rectangular, ftir_T, waveguide_T_te10, metal_T_skin_depth,
    arc_with_tunneling,
)

router = APIRouter(prefix="/tunnel", tags=["tunneling"])

# --------------------- Waveguide TE10 ---------------------
class WaveguideRequest(BaseModel):
    n: float = Field(..., gt=0, description="Filling refractive index (≈1 air)")
    a_mm: float = Field(..., gt=0, description="Broad dimension a (mm)")
    length_mm: float = Field(..., gt=0, description="Below-cutoff length (mm)")
    wavelength_nm: float = Field(..., gt=0, description="Vacuum wavelength (nm)")
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

class WaveguideResponse(BaseModel):
    T_wg: float
    arc: dict
    lambda_c_nm: float

@router.post("/waveguide", response_model=WaveguideResponse)
def waveguide_tunneling(body: WaveguideRequest):
    a_m = body.a_mm * 1e-3
    L_m = body.length_mm * 1e-3
    lam0_m = nm_to_m(body.wavelength_nm)
    T = waveguide_T_te10(body.n, a_m, lam0_m, L_m)
    lambda_c_m = (2.0 * a_m) / body.n  # cutoff approx λc ≈ 2a/n
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)
    return {"T_wg": T, "arc": arc, "lambda_c_nm": lambda_c_m * 1e9}

# --------------------- Metal (skin-depth) -----------------
class MetalRequest(BaseModel):
    sigma_S_per_m: float = Field(..., gt=0, description="Conductivity S/m (Cu~5.8e7)")
    freq_Hz: float = Field(..., gt=0, description="Frequency (Hz)")
    thickness_um: float = Field(..., ge=0, description="Thickness (μm)")
    mu_r: float = Field(1.0, gt=0, description="Relative permeability")
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

class MetalResponse(BaseModel):
    T_metal: float
    arc: dict
    skin_depth_um: float

@router.post("/metal", response_model=MetalResponse)
def metal_tunneling(body: MetalRequest):
    t_m = body.thickness_um * 1e-6
    T = metal_T_skin_depth(body.sigma_S_per_m, body.freq_Hz, t_m, mu_r=body.mu_r)
    omega = 2.0 * math.pi * body.freq_Hz
    # reuse skin_depth from modules if you expose it, else recompute here
    mu0 = 4e-7 * math.pi
    delta = math.sqrt(2.0 / (mu0 * body.mu_r * body.sigma_S_per_m * omega))
    arc = arc_with_tunneling(body.R_free, body.A, body.C, T_tun=T, alpha=body.alpha)
    return {"T_metal": T, "arc": arc, "skin_depth_um": delta * 1e6}

# --------------------- Plot sweeps ------------------------
class PlotRequest(BaseModel):
    model: str = Field(..., description="qm | ftir | waveguide | metal | multi")
    d_min: float = Field(..., gt=0, description="Start of sweep")
    d_max: float = Field(..., gt=0, description="End of sweep")
    points: int = Field(200, gt=1, le=5000)

    # QM
    barrier_height_eV: float | None = None
    particle_energy_eV: float | None = None
    mass_kg: float | None = None

    # FTIR
    n1: float | None = None
    n2: float | None = None
    theta_deg: float | None = None
    wavelength_nm: float | None = None

    # WAVEGUIDE
    n: float | None = None
    a_mm: float | None = None
    wavelength_nm_wg: float | None = None

    # METAL
    sigma_S_per_m: float | None = None
    freq_Hz: float | None = None
    mu_r: float | None = 1.0

    # MULTI
    curves: list[str] | None = None

    # ARC overlay
    R_free: float = 0.0
    A: float = 0.0
    C: float = 0.15
    alpha: float = 1.0

    fmt: str = Field("png", pattern="^(png|svg)$")

@router.post("/plot")
def tunnel_plot(body: PlotRequest):
    import numpy as np

    if body.d_max <= body.d_min:
        raise HTTPException(400, "d_max must be > d_min")
    ds = np.linspace(body.d_min, body.d_max, body.points)

    def sweep_qm(ds_nm):
        if any(v is None for v in [body.barrier_height_eV, body.particle_energy_eV]):
            raise HTTPException(400, "QM requires barrier_height_eV and particle_energy_eV")
        m = body.mass_kg if body.mass_kg else M_ELECTRON
        V0 = eV_to_J(body.barrier_height_eV); E = eV_to_J(body.particle_energy_eV)
        Ts = [ (1.0 if E >= V0 else qm_T_rectangular(m, V0, E, d_nm*1e-9)) for d_nm in ds_nm ]
        return np.asarray(Ts), "Barrier width d (nm)"

    def sweep_ftir(ds_nm):
        if any(v is None for v in [body.n1, body.n2, body.theta_deg, body.wavelength_nm]):
            raise HTTPException(400, "FTIR requires n1, n2, theta_deg, wavelength_nm")
        theta = deg_to_rad(body.theta_deg); lam = nm_to_m(body.wavelength_nm)
        Ts = [ ftir_T(body.n1, body.n2, theta, lam, gap_nm*1e-9) for gap_nm in ds_nm ]
        return np.asarray(Ts), "Gap d (nm)"

    def sweep_waveguide(ds_mm):
        if any(v is None for v in [body.n, body.a_mm, body.wavelength_nm_wg]):
            raise HTTPException(400, "waveguide requires n, a_mm, wavelength_nm_wg")
        a_m = body.a_mm * 1e-3; lam0 = nm_to_m(body.wavelength_nm_wg)
        Ts = [ waveguide_T_te10(body.n, a_m, lam0, L_mm*1e-3) for L_mm in ds_mm ]
        return np.asarray(Ts), "Below-cutoff length L (mm)"

    def sweep_metal(ds_um):
        if any(v is None for v in [body.sigma_S_per_m, body.freq_Hz]):
            raise HTTPException(400, "metal requires sigma_S_per_m and freq_Hz")
        mu_r = 1.0 if body.mu_r is None else body.mu_r
        Ts = [ metal_T_skin_depth(body.sigma_S_per_m, body.freq_Hz, t_um*1e-6, mu_r=mu_r) for t_um in ds_um ]
        return np.asarray(Ts), "Metal thickness t (μm)"

    # Single model
    if body.model != "multi":
        if body.model == "qm":
            Ts, xlabel = sweep_qm(ds)
        elif body.model == "ftir":
            Ts, xlabel = sweep_ftir(ds)
        elif body.model == "waveguide":
            Ts, xlabel = sweep_waveguide(ds)
        elif body.model == "metal":
            Ts, xlabel = sweep_metal(ds)
        else:
            raise HTTPException(400, "model must be qm | ftir | waveguide | metal | multi")

        Rprime = body.R_free + body.alpha * Ts
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(ds, Ts, lw=2, label="T(d)")
        ax.plot(ds, Rprime, lw=1.5, ls="--", label="R' = R_free + α T")
        ax.axhline(body.A + body.C, color="gray", lw=1, ls=":")
        ax.set_xlabel(xlabel); ax.set_ylabel("Transmission / Return")
        ax.set_title(f"Tunneling sweep — {body.model.upper()}")
        ax.set_ylim(0, 1.05); ax.grid(True, alpha=0.3); ax.legend()

    # Multi overlay
    else:
        curves = body.curves or ["qm", "ftir", "waveguide", "metal"]
        fig, ax = plt.subplots(figsize=(9,5))
        labels = []
        for cv in curves:
            c = cv.lower()
            if c == "qm":
                Ts, _ = sweep_qm(ds)
                ax.plot(ds, Ts, lw=2); labels.append("QM (d nm)")
            elif c == "ftir":
                Ts, _ = sweep_ftir(ds)
                ax.plot(ds, Ts, lw=2); labels.append("FTIR (gap nm)")
            elif c == "waveguide":
                Ts, _ = sweep_waveguide(ds)
                ax.plot(ds, Ts, lw=2); labels.append("WG (L mm)")
            elif c == "metal":
                Ts, _ = sweep_metal(ds)
                ax.plot(ds, Ts, lw=2); labels.append("Metal (t μm)")
            else:
                raise HTTPException(400, f"unknown curve: {cv}")
        ax.set_xlabel("Sweep variable (per-curve units)")
        ax.set_ylabel("Transmission T")
        ax.set_title("Tunneling models — multi-curve overlay")
        ax.set_ylim(0, 1.05); ax.grid(True, alpha=0.3)
        ax.legend(labels, loc="best")

    buf = BytesIO()
    media = "image/svg+xml" if body.fmt == "svg" else "image/png"
    fmt = "svg" if body.fmt == "svg" else "png"
    fig.savefig(buf, format=fmt, dpi=(160 if fmt=="png" else None), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type=media)