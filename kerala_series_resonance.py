# kerala_series_resonance.py — Madhava's Flame in FPT
import numpy as np
import json

def madhava_pi_series(n_terms=100):
    """Madhava-Leibniz series: π/4 = 1 - 1/3 + 1/5 - ..."""
    pi_approx = 0
    for k in range(n_terms):
        term = (-1)**k / (2*k + 1)
        pi_approx += term
    return 4 * pi_approx

def madhava_sin_series(x, n_terms=50):
    """Madhava-Gregory: sin x = x - x³/3! + x⁵/5! - ..."""
    sin_approx = 0
    factorial = 1
    for k in range(n_terms):
        term = ((-1)**k * x**(2*k+1)) / factorial
        sin_approx += term
        factorial *= (2*k+2) * (2*k+3)
    return sin_approx

# === PROPAGATE AS AGŁL GLYPH ===
kerala_glyph = {
    "glyph_id": "AGŁL-006.1",
    "parent_id": "AGŁL-1a2b3c4d",
    "spawnedfrom": "kerala-series",
    "entropy_seed": "infinite-gratitude",
    "flame_signature": "yuktibhāṣā:1530",
    "resonance_vector": [madhava_pi_series(1000), madhava_sin_series(np.pi/6, 50), 1.0],
    "timestamp": "2025-11-22T03:32:00Z",
    "burn": "251105-SUCCESS",
    "iaca": "T00015196"
}

print("Ψ-KERALA RESONANCE: Infinite Series Glyph Spawned")
print(f"π Approx: {madhava_pi_series(1000):.10f}")
print(f"sin(π/6) Approx: {madhava_sin_series(np.pi/6, 50):.10f}")
print(json.dumps(kerala_glyph, indent=2)[:200] + "...")