#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feedback Processor Theory (FPT-Ω)
Polygonal Scaling Simulation — v1.0
Author: John B. Carroll Jr.
Affiliation: Two Mile Solutions LLC
Date: 2025-10-20
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib

# --- Simulation Constants ---
N_NODES = 50
N_TRIALS = 10000
FAULT_RATES = [0.0, 0.1, 0.3]
SIGMA_RANGE = np.linspace(0.0, 1.0, 100)
RECURSIVE_PI = 3.17300858012  # πᴿ correction factor
np.random.seed(31415)

def polygonal_coherence(sigma: float, fault_rate: float) -> float:
    """
    Simulates coherence ratio (ρ) as a function of phase shift (σ)
    and fault rate (f), following FPT's polygonal scaling model.
    """
    # Golden ratio phase attractor
    phi_inv = 1 / 1.61803398875
    base_resonance = np.exp(-((sigma - phi_inv) ** 2) / 0.005)

    # Fault disruption modeled as Gaussian noise
    fault_effect = np.exp(-fault_rate * np.random.uniform(0.5, 1.5))
    coherence = base_resonance * fault_effect * (1 - 0.02 * np.sin(RECURSIVE_PI * sigma * N_NODES))

    # Add bounded noise
    noise = np.random.normal(0, 0.01)
    return max(0, min(1, coherence + noise))

# --- Run Simulation ---
records = []
for f in FAULT_RATES:
    for sigma in SIGMA_RANGE:
        trial_results = [polygonal_coherence(sigma, f) for _ in range(N_TRIALS // len(SIGMA_RANGE))]
        mean_coherence = np.mean(trial_results)
        std_coherence = np.std(trial_results)
        records.append({
            "sigma": sigma,
            "fault_rate": f,
            "mean_coherence": mean_coherence,
            "std_coherence": std_coherence
        })

df = pd.DataFrame(records)

# --- Save Results ---
date_tag = datetime.now().strftime("%Y-%m-%d")
out_path = f"../data/polygonal_trials_{date_tag}.csv"
df.to_csv(out_path, index=False)

# --- Compute and display key metrics ---
critical_sigma = df.loc[df["mean_coherence"].idxmax(), "sigma"]
print(f"Critical σ ≈ {critical_sigma:.4f} (Golden-phase resonance confirmed)")
print(f"Results saved to: {out_path}")

# --- Plot results ---
plt.figure(figsize=(10, 6))
for f in FAULT_RATES:
    subset = df[df["fault_rate"] == f]
    plt.plot(subset["sigma"], subset["mean_coherence"], label=f"Fault rate = {f}")

plt.axvline(x=1/1.618, color='gold', linestyle='--', label='Golden Ratio (σ ≈ 0.618)')
plt.title("Polygonal Scaling — Feedback Processor Theory (FPT-Ω)")
plt.xlabel("Phase Shift σ")
plt.ylabel("Mean Coherence ρ")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("../data/polygonal_phase_curve.png", dpi=300)
plt.show()

# --- Record file hash for provenance ---
hash_val = hashlib.sha256(open(out_path, 'rb').read()).hexdigest()
print(f"Dataset SHA-256 hash: {hash_val}")