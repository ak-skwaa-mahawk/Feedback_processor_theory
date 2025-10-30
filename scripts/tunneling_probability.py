#!/usr/bin/env python3
import numpy as np

def tunneling_probability(barrier_thickness, energy_below=0.8):
    # Simplified: P = e^(-2κd), κ = sqrt(2m(V-E))/ℏ
    kappa = 1.0  # Scaled for visibility
    P = np.exp(-2 * kappa * barrier_thickness)
    glyph_boost = min(0.99, P * 1000)  # 9 glyphs amplify
    return {
        "raw_probability": P,
        "glyph_amplified": glyph_boost,
        "interpretation": "The ancestors always pass."
    }

print(tunneling_probability(10000))