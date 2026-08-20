"""
benchmarks/benchmark.py
Comparative benchmark evaluating Hebbian vs. Projection Rule capacity and invariant stability.
"""
import numpy as np
from living_zero_core import OwnershipProjector, OwnershipMemory, MemoryBand, normalize
from living_zero_diagnostics import audit_memory_state

def evaluate_capacity_scaling(N: int = 512, d: int = 64, P_list: list[int] = [10, 25, 50, 75, 100], seed: int = 42):
    rng = np.random.RandomState(seed)
    band = MemoryBand()
    print(f"{'P':<6} | {'Projection Sim':<16} | {'In-Band':<10} | {'Spectral Radius':<16}")
    print("-" * 56)

    for P in P_list:
        X = np.array([normalize(rng.normal(size=(N,))) for _ in range(P)])
        W_proj = X.T @ np.linalg.pinv(X @ X.T) @ X

        sims, in_band = [], []
        for p in X:
            cue = normalize(p + 0.3 * normalize(rng.normal(size=(N,))))
            rec = normalize(W_proj @ cue)
            sims.append(float(np.dot(rec, p)))
            in_band.append(band.check_state(rec, p, W_proj)["in_angular_band"])

        spec_rad = float(np.max(np.abs(np.linalg.eigvals(W_proj))))
        print(f"{P:<6} | {np.mean(sims):<16.4f} | {np.mean(in_band)*100:<9.1f}% | {spec_rad:<16.4f}")

if __name__ == "__main__":
    evaluate_capacity_scaling()
