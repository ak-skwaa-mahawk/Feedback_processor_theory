"""
sound_resonance.py
Two Mile Solutions LLC (CC0-1.0)

Stellar Vacuum Resonance model:
- Unifies sound & light as one oscillatory medium.
- Implements Attenuation–Return Criterion (ARC):
      A(r,f) * R(f) >= C  -> perception/coherence event
- Provides simple utilities for simulation and color/tone mapping.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Iterable, Tuple, Dict, List

# ---------- Core attenuation model ----------

def attenuation(r_m: float, f_hz: float, alpha: float = None, beta: float = None) -> float:
    """
    Path attenuation A(r,f) = exp(-alpha(f)*r) * 1/(1 + beta(f)*r^2)
    alpha ~ absorptive/phase delay term (per meter)
    beta  ~ geometric/scatter term (per m^2)
    """
    # Frequency-scaled defaults: higher frequencies lose more (tune to medium)
    if alpha is None:
        # mild absorption rising with f (normalized at kHz scale)
        alpha = 1e-8 * max(f_hz, 0.0) ** 0.5
    if beta is None:
        # small geometric term
        beta = 1e-12 * max(f_hz, 0.0) ** 0.25

    return math.exp(-alpha * r_m) * (1.0 / (1.0 + beta * (r_m ** 2)))


def return_resonance(f_hz: float, bands: Dict[str, Tuple[float, float]] = None) -> float:
    """
    Observer 'return' R(f): band-wise sensitivity curve merged into a single scalar.
    Defaults approximate human sensitivity bands (rough heuristic):
      - audio: 20–20k Hz (peak ~ 3k)
      - vision: 4e14–7.5e14 Hz (blue/green stronger return)
      - biophoton IR: 1e13–1e14 Hz (weak but present)
    Returns normalized 0..1
    """
    if bands is None:
        bands = {
            "audio": (20.0, 2.0e4),
            "vision": (4.0e14, 7.5e14),
            "bio_ir": (1.0e13, 1.0e14),
        }

    def bell(x, mu, sigma):
        if sigma <= 0:
            return 0.0
        z = (x - mu) / sigma
        return math.exp(-0.5 * z * z)

    r_audio = 0.0
    lo, hi = bands["audio"]
    if lo <= f_hz <= hi:
        # peak around ~3 kHz
        r_audio = bell(math.log10(f_hz), math.log10(3000.0), 0.25)

    r_vis = 0.0
    lo, hi = bands["vision"]
    if lo <= f_hz <= hi:
        # favor green-blue; map frequency to a bell over visible range
        # center at ~5.5e14 (green), sigma ~0.12e14
        r_vis = bell(f_hz, 5.5e14, 0.12e14)

    r_ir = 0.0
    lo, hi = bands["bio_ir"]
    if lo <= f_hz <= hi:
        r_ir = bell(math.log10(f_hz), math.log10(3.0e13), 0.35)

    # Combine with weights; tune as needed
    r = 0.6 * r_vis + 0.35 * r_audio + 0.05 * r_ir
    return max(0.0, min(1.0, r))


def arc_score(r_m: float, f_hz: float, C: float = 0.15) -> Tuple[float, bool]:
    """
    Compute ARC = A(r,f)*R(f), and return (score, passes_threshold)
    """
    A = attenuation(r_m, f_hz)
    R = return_resonance(f_hz)
    score = A * R
    return score, (score >= C)


# ---------- Helpers: mapping frequency to color/tone ----------

def color_from_frequency(f_hz: float) -> Tuple[int, int, int]:
    """
    Approximate visible color for f in ~[4.0e14, 7.5e14] Hz; otherwise grayscale by proximity.
    """
    f_min, f_max = 4.0e14, 7.5e14
    if f_hz <= f_min:
        g = 80
        return (g, g, g)
    if f_hz >= f_max:
        g = 170
        return (g, g, g)

    # Map to wavelength approx 400–750 nm for simple RGB ramps (heuristic)
    c = 2.99792458e8
    lam = c / f_hz * 1e9  # nm
    # crude piecewise mapping
    if lam < 450:       # violet/blue
        return (80, 110, 220)
    elif lam < 495:     # cyan
        return (80, 200, 200)
    elif lam < 570:     # green
        return (90, 220, 120)
    elif lam < 590:     # yellow
        return (230, 210, 80)
    elif lam < 620:     # orange
        return (240, 150, 60)
    else:               # red
        return (220, 80, 80)


def audible_from_frequency(f_hz: float) -> float:
    """
    Return 0..1 audibility proxy within 20–20k Hz (A-weighting-inspired).
    """
    if f_hz < 20.0 or f_hz > 2.0e4:
        return 0.0
    # emphasize 1–5 kHz band
    x = math.log10(f_hz)
    peak = math.log10(3000.0)
    sigma = 0.35
    return math.exp(-0.5 * ((x - peak) / sigma) ** 2)


# ---------- Simulation utilities ----------

@dataclass
class Medium:
    name: str
    alpha_scale: float = 1.0
    beta_scale: float = 1.0

    def A(self, r_m: float, f_hz: float) -> float:
        return attenuation(r_m, f_hz, alpha=1e-8 * self.alpha_scale * (f_hz ** 0.5),
                           beta=1e-12 * self.beta_scale * (f_hz ** 0.25))


HELIO = Medium("heliosphere", alpha_scale=0.6, beta_scale=0.8)
AIR   = Medium("atmosphere",  alpha_scale=1.0, beta_scale=1.0)
VAC   = Medium("interstellar",alpha_scale=0.25, beta_scale=0.5)


def simulate_path(r_m: float, f_hz: float, medium: Medium = AIR, C: float = 0.15) -> Dict:
    """
    Simulate a single hop through a medium and evaluate ARC.
    """
    A = medium.A(r_m, f_hz)
    R = return_resonance(f_hz)
    score = A * R
    color = color_from_frequency(f_hz)
    audible = audible_from_frequency(f_hz)
    return {
        "medium": medium.name,
        "distance_m": r_m,
        "frequency_hz": f_hz,
        "attenuation": A,
        "return": R,
        "arc": score,
        "passes": score >= C,
        "rgb": color,
        "audible_0_1": audible,
    }


def sweep_frequencies(r_m: float, freqs_hz: Iterable[float], medium: Medium = AIR, C: float = 0.15) -> List[Dict]:
    return [simulate_path(r_m, f, medium=medium, C=C) for f in freqs_hz]


# ---------- CLI demo ----------

if __name__ == "__main__":
    demo = [
        ("audio 1kHz, air, 10m", simulate_path(10.0, 1_000.0, AIR)),
        ("audio 3kHz, air, 10m", simulate_path(10.0, 3_000.0, AIR)),
        ("visible green, air, 10m", simulate_path(10.0, 5.5e14, AIR)),
        ("visible red, helio, 1e6m", simulate_path(1e6, 4.5e14, HELIO)),
        ("UV, interstellar, 1e9m", simulate_path(1e9, 9.0e14, VAC)),
    ]
    for label, res in demo:
        print(f"\n[{label}]")
        for k, v in res.items():
            print(f"  {k}: {v}")