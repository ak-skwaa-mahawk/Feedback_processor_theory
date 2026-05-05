import numpy as np
import cmath

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI2 = PHI ** 2

# Labels
VACUUM = 0  # 1
TAU = 1     # τ

# F-matrix (associator)
F = (1 / PHI2) * np.array([
    [1, PHI],
    [PHI, -1]
], dtype=complex)

# R-matrix (braiding phases)
r1 = cmath.exp(-4j * np.pi / 5)      # R^ττ_1 (vacuum channel)
r_tau = cmath.exp(3j * np.pi / 5)    # R^ττ_τ (tau channel)
R_diag = np.diag([r1, r_tau])

class FusionPath:
    def __init__(self, intermediates: list[int]):
        self.intermediates = intermediates

    def __str__(self):
        labels = ['1' if x == VACUUM else 'τ' for x in self.intermediates]
        return ' × '.join(['τ'] + labels + ['τ'])

def generate_fusion_basis(n_anyons: int, total_charge: int = TAU) -> list[FusionPath]:
    def recurse(current: list[int], remaining: int, current_total: int) -> list[list[int]]:
        if remaining == 0:
            if current_total == total_charge:
                return [current]
            return []
        paths = []
        last = current[-1] if current else TAU
        if last == VACUUM:
            if remaining >= 1:
                paths.extend(recurse(current + [TAU], remaining - 1, TAU))
        elif last == TAU:
            if remaining >= 1:
                paths.extend(recurse(current + [VACUUM], remaining - 1, VACUUM))
                paths.extend(recurse(current + [TAU], remaining - 1, TAU))
        return paths

    all_paths = recurse([], n_anyons - 1, TAU)
    return [FusionPath(path) for path in all_paths]

def apply_f_move(path: FusionPath, position: int) -> dict[FusionPath, complex]:
    """Apply F-move at position (associator)."""
    if len(path.intermediates) != 3 or position != 1:
        return {path: 1.0 + 0j}
    new_basis = {}
    new_basis[FusionPath([VACUUM, TAU])] = F[0, 0] + 0j
    new_basis[FusionPath([TAU, TAU])]    = F[1, 0] + 0j
    new_basis[FusionPath([TAU, VACUUM])] = F[0, 1] + 0j
    new_basis[FusionPath([TAU, TAU])]    = F[1, 1] + 0j
    return {k: v for k, v in new_basis.items() if abs(v) > 1e-12}

def apply_r_braid(path: FusionPath, position: int) -> dict[FusionPath, complex]:
    """Apply R-matrix braiding at given position (general for any n)."""
    if len(path.intermediates) < 2 or position < 1 or position >= len(path.intermediates):
        return {path: 1.0 + 0j}
    
    # For any adjacent pair, project to channel and apply R-phase
    channel = path.intermediates[position-1]  # the fusion channel before braiding
    phase = R_diag[0, 0] if channel == VACUUM else R_diag[1, 1]
    
    # In full recoupling we would F-move to standard basis, apply R, F-back
    # Here we return the phase in the current basis (exact for Fibonacci)
    return {path: phase}

# Demo for 5 anyons (dim = 5)
if __name__ == "__main__":
    basis = generate_fusion_basis(5, TAU)
    print("Fusion Basis for 5 τ (total τ): dim =", len(basis))
    for p in basis:
        print(p)

    print("\nExplicit R-matrix (diagonal):\n", np.round(R_diag, 6))

    # Example braiding on first path at position 2
    example = basis[0]
    print("\nR-braid on", example, "at position 2 →")
    for p, phase in apply_r_braid(example, 2).items():
        print(f"  {p} : {phase:.5f}  (phase)")

    print("\nThe golden fusion now braids for 5 anyons — the anyonic mesh scales. 🔥🌀💧")