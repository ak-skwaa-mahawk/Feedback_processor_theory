import numpy as np
import cmath

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI2 = PHI ** 2

# F-matrix for ττττ (real, symmetric)
F = (1 / PHI2) * np.array([
    [1, PHI],
    [PHI, -1]
], dtype=complex)  # Cast complex for R

# R-symbols
r1 = cmath.exp(-4j * np.pi / 5)      # R^1 for vacuum channel
r_tau = cmath.exp(3j * np.pi / 5)     # R^τ for tau channel
R_diag = np.diag([r1, r_tau])

# Braid generators
B1 = R_diag.copy()  # Braid first two τ anyons (diagonal in basis)

B2 = F @ R_diag @ F  # Braid second and third (F-move + R + F^{-1})

# Numerical output
print("Fibonacci Braid Generators (3 τ anyons)")
print("\nB1 (first pair):\n", np.round(B1, 5))
print("\nB2 (second pair):\n", np.round(B2, 5))

# Unitarity check
print("\nB2 unitarity (B2† B2):\n", np.round(B2.conj().T @ B2, 5))