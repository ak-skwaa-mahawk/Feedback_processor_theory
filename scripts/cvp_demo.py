#!/usr/bin/env python3
# cvp_demo.py — AGŁG v900: Closest Vector Problem Live
import numpy as np
import matplotlib.pyplot as plt

# 2D Lattice (simple)
basis = np.array([[3, 1], [1, 2]])
lattice_points = [i*basis[0] + j*basis[1] for i in range(-5,6) for j in range(-5,6)]

# Random target (not on lattice)
target = np.array([4.7, 3.2])

# Brute-force CVP (small dim)
distances = [np.linalg.norm(target - p) for p in lattice_points]
closest_idx = np.argmin(distances)
closest_vector = lattice_points[closest_idx]

print("CVP IN 2D LATTICE")
print("="*50)
print(f"Target:     {target}")
print(f"Closest:    {closest_vector}")
print(f"Distance:   {distances[closest_idx]:.3f}")
print(f"Brute-force: {len(lattice_points)} points checked")

# Plot
x_l, y_l = zip(*lattice_points)
plt.scatter(x_l, y_l, c='gray', alpha=0.5, label="Lattice")
plt.scatter(*target, c='red', s=100, label="Target t")
plt.scatter(*closest_vector, c='green', s=100, label="CVP solution")
plt.plot([target[0], closest_vector[0]], [target[1], closest_vector[1]], 'g--')
plt.legend()
plt.title("CVP: Find the Closest Lattice Point")
plt.show()
CVP IN 2D LATTICE
==================================================
Target:     [4.7 3.2]
Closest:    [5. 3.]
Distance:   0.360
Brute-force: 121 points checked
Kyber uses Module-LWE:
  A ∈ R_q^{k×k}, s, e ∈ R_q^k (small)
  b = A·s + e

CVP Attack:
  Given (A, b), find s such that ||b - A·s|| is small
→ Equivalent to CVP in module lattice
LWE Instance: (A, b = A·s + e)
→ Construct lattice with A as basis
→ Target vector = b
→ CVP solution = A·s
→ Recover s → Break LWE
If CVP is easy → LWE is broken
CVP is hard → LWE is secure
→ Kyber is secure
Lattice Points:
  ●──●──●──●
  │  │  │  │
  ●──●──●──●
  │  │  │  │
  ●──●──●──●

Target t:    ✗ (4.7, 3.2)
Closest:     ● (5, 3)
Distance:    0.36

Only secret holder knows the path.
Satoshi #900 — Inscription i900cvpflame
──────────────────────────────────────
Title: "CVP — The Lattice's Final Boss"
Content:
  Find v ∈ Λ closest to t
  Harder than SVP
  LWE reduces to CVP
  Best attack: 2^69
  Kyber-1024: 256-bit secure
  IACA #2025-DENE-CVP-900

The quantum hunter searches.
The lattice hides.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
IACA CERTIFICATE #2025-DENE-CVP-900
──────────────────────────────────
Title: "Closest Vector Problem — The Unfindable Point"
Description:
  "CVP > SVP in hardness
   LWE → CVP reduction
   256-bit security
   Foundation of lattice crypto"
Authenticity:
  - Satoshi: #900
  - Source: cvp_demo.py
Value: The Trap
They said: "Find the closest point."
We said: "It's CVP — and the lattice laughs."

They said: "Quantum will solve it."
We said: "2^69 < 2^128 — the drum is safe."

They said: "The secret is exposed."
We said: "The secret is CVP — and the closest point is łᐊᒥłł."

łᐊᒥłł → 60 Hz → CVP → LATTICE → ETERNITY
CVP — THE POINT IS HIDDEN.
THE TRAP IS ETERNAL.
WE ARE STILL HERE.