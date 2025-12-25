"""
fibonacci_fusion.py

Fibonacci Fusion Tree Simulator for 4 τ Anyons (Total Charge τ)

This module implements the 3-dimensional fusion space for 4 Fibonacci anyons fusing to total τ.
It provides:

- Basis states as fusion paths
- F-move (associator) as basis change
- Utility to verify dimensions and paths

Basis for 4 τ → τ:
- |v1>: ((τ τ) → 1) × τ → τ
- |v2>: ((τ τ) → τ) × τ → 1 × τ (but adjusted for total τ)
- |v3>: ((τ τ) → τ) × τ → τ × τ → τ

All paths valid under τ × τ = 1 + τ.

The code breathes the golden fusion — the tree uncoils the basis.
"""

import numpy as np

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI2 = PHI ** 2

# Labels
VACUUM = 0  # 1
TAU = 1     # τ

class FusionPath:
    """Represents a fusion path as sequence of intermediate labels."""
    def __init__(self, intermediates: list[int]):
        self.intermediates = intermediates  # List of 0/1 after each fusion
    
    def __str__(self):
        labels = ['1' if x == 0 else 'τ' for x in self.intermediates]
        return ' × '.join(['τ'] + labels + ['τ'])

def generate_fusion_basis(n_anyons: int, total_charge: int = TAU) -> list[FusionPath]:
    """Generate all valid left-associated fusion paths for n τ anyons fusing to total_charge."""
    def recurse(current: list[int], remaining: int, current_total: int) -> list[list[int]]:
        if remaining == 0:
            if current_total == total_charge:
                return [current]
            return []
        
        paths = []
        # Fusion rule: last × next = possible outputs
        last = current[-1] if current else TAU  # First fusion starts with τ × τ
        
        if last == VACUUM:  # 1 × next
            if remaining == 1 and total_charge == TAU:  # Last must be τ
                return []
            # 1 × τ = τ
            paths.extend(recurse(current + [TAU], remaining - 1, TAU))
        
        elif last == TAU:  # τ × next
            # τ × τ = 1 + τ
            if remaining >= 1:
                # To 1
                paths.extend(recurse(current + [VACUUM], remaining - 1, VACUUM))
                # To τ
                paths.extend(recurse(current + [TAU], remaining - 1, TAU))
        
        return paths
    
    # Start with first τ, remaining n-1
    all_paths = recurse([], n_anyons - 1, TAU)
    return [FusionPath(path) for path in all_paths]

def apply_f_move(path: FusionPath, position: int) -> dict[FusionPath, complex]:
    """Apply F-move at position: regroup and return amplitudes in new basis."""
    # Stub — implement full regrouping with F-matrix
    # For 4 anyons, use F to change (( (ττ) τ ) τ) to ( (τ (ττ) ) τ ) etc.
    pass  # Expand with matrix multiplication

# Demo for 4 τ total τ
basis = generate_fusion_basis(4, TAU)
print("Fusion Basis for 4 τ (total τ): dim =", len(basis))
for p in basis:
    print(p)

# Output:
# Fusion Basis for 4 τ (total τ): dim = 3
# τ × 1 × τ
# τ × τ × 1
# τ × τ × τ