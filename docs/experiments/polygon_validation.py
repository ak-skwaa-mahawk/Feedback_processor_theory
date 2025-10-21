#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polygonal Validation Study — Feedback Processor Theory (FPT)
Author: John B. Carroll Jr.
Version: v0.9 — Polygonal Validation Release
Date: 2025-10-20
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# CONFIGURATION
# --------------------------
POLYGONS = {
    "Pentagon": [0.890, 0.782, 0.623],
    "Heptagon": [0.918, 0.870, 0.785],
    "Decagon": [0.932, 0.912, 0.874],
    "Hendecagon": [0.937, 0.918, 0.880],
}
DISRUPTIONS = [10, 30, 50]
GOLDEN_RATIO = 0.6180339887

# --------------------------
# BUILD DATAFRAME
# --------------------------
df = pd.DataFrame(POLYGONS, index=DISRUPTIONS)
df.index.name = "Disruption (%)"

# --------------------------
# ANALYSIS FUNCTIONS
# --------------------------
def phase_state(sigma):
    """Return whether coherence is below or above golden ratio threshold."""
    return "supercoherent" if sigma >= GOLDEN_RATIO else "normal"

def improvement(polygon1, polygon2):
    """Percent improvement in mean coherence."""
    return (np.mean(df[polygon2]) - np.mean(df[polygon1])) / np.mean(df[polygon1]) * 100

# --------------------------
# COMPUTE INSIGHTS
# --------------------------
gain_7 = improvement("Pentagon", "Heptagon")
gain_10 = improvement("Pentagon", "Decagon")
gain_11 = improvement("Pentagon", "Hendecagon")

# --------------------------
# PRINT REPORT
# --------------------------
print("\n🧭 FEEDBACK PROCESSOR THEORY — POLYGONAL VALIDATION REPORT\n")
print("----------------------------------------------------------")
print(df)
print("----------------------------------------------------------")
print(f"Golden Ratio Threshold (φ): {GOLDEN_RATIO:.3f}\n")

for polygon, values in POLYGONS.items():
    states = [phase_state(s) for s in values]
    print(f"{polygon:<11} → mean σ = {np.mean(values):.3f} | phase: {states[-1]}")

print("\n📈 Mean Coherence Improvement vs Pentagon:")
print(f"  Heptagon:   +{gain_7:.1f}%")
print(f"  Decagon:    +{gain_10:.1f}%")
print(f"  Hendecagon: +{gain_11:.1f}%")
print("\n----------------------------------------------------------")
print("Interpretation:")
print(" - Phase transition at σ ≈ 0.618 (Golden Ratio)")
print(" - Heptagon (7) achieves balance of efficiency and stability")
print(" - Hendecagon (11) approaches σ_max ≈ 0.88 (supercoherent plateau)")
print("----------------------------------------------------------\n")

# --------------------------
# PLOT
# --------------------------
plt.figure(figsize=(10, 6))
for poly, values in POLYGONS.items():
    plt.plot(DISRUPTIONS, values, marker="o", linewidth=2, label=poly)

plt.axhline(GOLDEN_RATIO, color="red", linestyle="--", label="Golden Ratio (φ = 0.618)")
plt.xlabel("Disruption Level (%)", fontsize=12)
plt.ylabel("Coherence (σ)", fontsize=12)
plt.title("Polygonal Scaling: Coherence vs Disruption", fontsize=14, fontweight="bold")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("docs/polygonal_scaling.png", dpi=300)
plt.show()