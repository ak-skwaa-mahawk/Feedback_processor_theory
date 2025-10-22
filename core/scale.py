# core/scale.py
from __future__ import annotations
import math
from decimal import Decimal, getcontext
from typing import Iterable, List, Tuple

from .constants import PLANCK_LENGTH_M, SCALE_STEP, DEFAULT_TOP_BANDS

# use high precision for exponentiation and division
getcontext().prec = 60


def length_at_band(n: int) -> Decimal:
    """Return geometric scale length L(n) = ℓ_p * S^n in meters (Decimal)."""
    return PLANCK_LENGTH_M * (SCALE_STEP ** int(n))


def band_for_length(L_m: Decimal | float) -> int:
    """
    Map a length (meters) to the nearest band index n.
    L <= ℓ_p → 0
    """
    L = Decimal(str(L_m))
    if L <= PLANCK_LENGTH_M:
        return 0
    # n = log_{S}(L / ℓ_p)
    n_real = (L / PLANCK_LENGTH_M).ln() / SCALE_STEP.ln()
    return int(Decimal(n_real).to_integral_value(rounding=getcontext().rounding))


def band_for_score(resonance_score: float, top_bands: int = DEFAULT_TOP_BANDS) -> int:
    """
    Map resonance score r∈[-1, 1] into [0, top_bands], clamped and rounded.
    r=-1 → 0 (ℓ_p floor), r=+1 → top_bands (symbolic "−ℓ_p" top).
    """
    r = max(-1.0, min(1.0, float(resonance_score)))
    return int(round(((r + 1.0) * 0.5) * int(top_bands)))


def series(n0: int = 0, n1: int = DEFAULT_TOP_BANDS) -> List[Tuple[int, Decimal]]:
    """Generate [(n, L(n))] for n in [n0, n1]."""
    return [(n, length_at_band(n)) for n in range(int(n0), int(n1) + 1)]


def humanize_meters(L: Decimal, sig: int = 3) -> Tuple[str, str]:
    """
    Convert meters to a human-friendly string with unit (nm, μm, mm, m, km).
    Returns (value_str, unit_str), with ~sig significant digits.
    """
    Lf = float(L)
    if Lf == 0.0:
        return ("0", "m")
    absL = abs(Lf)
    if absL < 1e-6:
        val, unit = Lf * 1e9, "nm"
    elif absL < 1e-3:
        val, unit = Lf * 1e6, "μm"
    elif absL < 1:
        val, unit = Lf * 1e3, "mm"
    elif absL < 1e3:
        val, unit = Lf, "m"
    else:
        val, unit = Lf / 1e3, "km"

    # round to sig figs
    fmt = f"{{:.{sig}g}}"
    return (fmt.format(val), unit)


def annotate_resonance(resonance_score: float, top_bands: int = DEFAULT_TOP_BANDS) -> dict:
    """
    Build a stable annotation payload for API/UI.
    Includes floor (ℓ_p), top (symbolic "−ℓ_p"), and current band.
    """
    n = band_for_score(resonance_score, top_bands)
    Ln = length_at_band(n)
    floor = length_at_band(0)
    top = length_at_band(top_bands)

    hv, hu = humanize_meters(Ln, sig=4)
    fv, fu = humanize_meters(floor, sig=4)
    tv, tu = humanize_meters(top, sig=4)

    return {
        "resonance_score": float(resonance_score),
        "band_index": n,
        "length_m": str(Ln),  # keep raw as string for precision
        "length_human": {"value": hv, "unit": hu},

        "floor_marker": {
            "name": "ℓ_p (floor)",
            "band_index": 0,
            "length_m": str(floor),
            "length_human": {"value": fv, "unit": fu},
        },
        "top_marker": {
            "name": "−ℓ_p (top, symbolic)",
            "band_index": int(top_bands),
            "length_m": str(top),
            "length_human": {"value": tv, "unit": tu},
        },
        "scale": {
            "planck_length_m": str(PLANCK_LENGTH_M),
            "step": str(SCALE_STEP),
            "top_bands": int(top_bands),
        },
    }
