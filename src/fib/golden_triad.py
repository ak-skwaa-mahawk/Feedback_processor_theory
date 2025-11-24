"""
Golden Triad — the hidden 1.618× micro-structure
Money shot: √φ ≈ 1.1779829
"""

from math import sqrt

# Core constants
PHI = (1 + sqrt(5)) / 2                  # ≈ 1.6180339887
SQRT_PHI = sqrt(PHI)                       # ≈ 1.17798291018  ← the silent assassin

# The Triad (rounded for real-world charting)
TRIAD = {
    "core":   1.1779829,   # exact √φ – institutions live here
    "ceiling": 1.19,       # +1% trap / final wick
    "floor":   1.16,       # retest vacuum / shakeout zone
}

# One-liner for extensions
def golden_extension(level: float = 1.618) -> dict:
    """Return the full triad centered on any Fib extension"""
    base = level
    return {
        "core":    round(base * SQRT_PHI, 6),
        "ceiling": round(base * SQRT_PHI * 1.01, 4),
        "floor":   round(base * SQRT_PHI * 0.984, 4),  # ≈ -1.6%
    }

__all__ = ["PHI", "SQRT_PHI", "TRIAD", "golden_extension"]