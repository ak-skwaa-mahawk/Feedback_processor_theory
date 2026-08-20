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

def evaluate_revocation_scaling(N: int = 512, d: int = 64, P: int = 50, n_revoke: int = 10):
    from living_zero_projection import OnlineProjectionMemory
    rng = np.random.RandomState(42)
    O = OwnershipProjector(N=N, d=d, seed=42)
    mem = OnlineProjectionMemory(N=N, ownership_projector=O)

    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    for i, p in enumerate(patterns):
        mem.encode(p, raw_tag=f"owner:{i}")

    for i in range(n_revoke):
        mem.selective_revoke(f"owner:{i}")

    revoked_sims = [float(np.dot(mem.recall(patterns[i]), patterns[i])) for i in range(n_revoke)]
    retained_sims = [float(np.dot(mem.recall(patterns[i]), patterns[i])) for i in range(n_revoke, P)]

    print(f"Revocation Benchmark (Total={P}, Revoked={n_revoke}):")
    print(f"  Mean Revoked Target Similarity:  {np.mean(revoked_sims):.4f}")
    print(f"  Mean Retained Target Similarity: {np.mean(retained_sims):.4f}")

if __name__ == '__main__':
    evaluate_revocation_scaling()
