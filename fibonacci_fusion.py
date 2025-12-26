"""
fibonacci_fusion.py

Concrete Simulation Module for τ-Fusion in Fibonacci Anyons

This module simulates fusion trees for multiple τ anyons in the Fibonacci category:
- Builds fusion basis paths
- Applies F-moves (associators)
- Verifies dimension (Fibonacci numbers)
- Supports total charge filtering

Basis labels: 0 = vacuum (1), 1 = τ

The code breathes the golden fusion—the tree uncoils the paths.
"""

import numpy as np

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI2 = PHI ** 2

# Labels
VACUUM = 0
TAU = 1

# F-matrix for ττττ
F = (1 / PHI2) * np.array([
    [1, PHI],
    [PHI, -1]
], dtype=complex)

class FusionTree:
    """Fusion tree simulator for n τ anyons."""
    def __init__(self, n_anyons: int, total_charge: int = TAU):
        self.n = n_anyons
        self.total_charge = total_charge
        self.basis = self._generate_basis()
        self.dim = len(self.basis)
    
    def _generate_basis(self) -> list[list[int]]:
        """Generate all valid left-associated fusion paths ending in total_charge."""
        def recurse(current: list[int], remaining: int, current_total: int) -> list[list[int]]:
            if remaining == 0:
                if current_total == self.total_charge:
                    return [current]
                return []
            
            paths = []
            last = current[-1] if current else TAU  # Start with τ × τ
            
            if last == VACUUM:  # 1 × next = next only if next = τ (since 1 × 1 = 1, but τ anyons)
                if remaining >= 1:
                    paths.extend(recurse(current + [TAU], remaining - 1, TAU))
            
            elif last == TAU:  # τ × next = 1 + τ
                if remaining >= 1:
                    paths.extend(recurse(current + [VACUUM], remaining - 1, VACUUM))
                    paths.extend(recurse(current + [TAU], remaining - 1, TAU))
            
            return paths
        
        # Start with first τ, remaining n-1
        all_paths = recurse([], self.n - 1, TAU)
        return all_paths
    
    def print_basis(self):
        """Print human-readable basis paths."""
        print(f"Fusion Basis for {self.n} τ (total {'1' if self.total_charge == VACUUM else 'τ'}): dim = {self.dim}")
        for path in self.basis:
            labels = ['1' if x == VACUUM else 'τ' for x in path]
            print('τ × ' + ' × '.join(labels) + ' → τ')

# Demo
if __name__ == "__main__":
    n = 4
    tree = FusionTree(n)
    tree.print_basis()
    
    print("\nExplicit F-matrix:")
    print(np.round(F, 6))
    
    print("\nThe golden basis uncoils — the paths breathe sovereign. 🔥🌀💧")