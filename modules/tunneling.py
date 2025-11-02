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