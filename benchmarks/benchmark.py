"""
benchmarks/benchmark.py
Comprehensive capacity and invariant benchmark for Ownership Dynamics.
"""
import numpy as np
from living_zero_core import OwnershipProjector, OwnershipMemory, MemoryBand, normalize
from living_zero_diagnostics import audit_memory_state

def run_capacity_benchmark(N: int = 512, d: int = 64, P: int = 40, seed: int = 42):
    rng = np.random.RandomState(seed)
    O = OwnershipProjector(N=N, d=d, seed=seed)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)
    band = MemoryBand()

    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    tags = [f"owner:{i}" for i in range(P)]

    for p, t in zip(patterns, tags):
        mem.encode(p, raw_tag=t)

    # Invariant diagnostics audit
    audit = audit_memory_state(mem, tags[:min(10, P)], band)

    # Recall benchmark (50% noise)
    results = []
    in_band_count = 0
    for idx, p in enumerate(patterns):
        cue = normalize(p + 0.5 * normalize(rng.normal(size=(N,))))
        rec = mem.recall_iter(cue, steps=30, bias_tag=tags[idx], beta=3.0)
        sim = float(np.dot(normalize(rec), p))
        results.append(sim)
        status = band.check_state(rec, p, mem.W)
        if status["in_angular_band"]:
            in_band_count += 1

    return {
        "mean_similarity": float(np.mean(results)),
        "in_band_ratio": in_band_count / P,
        "audit": audit,
    }

if __name__ == "__main__":
    res = run_capacity_benchmark(N=512, d=64, P=40)
    print(f"Capacity Benchmark (N=512, P=40):")
    print(f"  Mean Similarity:    {res['mean_similarity']:.6f}")
    print(f"  In-Band Ratio:      {res['in_band_ratio'] * 100:.1f}%")
    print(f"  Spectral Radius:    {res['audit']['spectral_radius']:.6f}")
    print(f"  Projector Residual: {res['audit']['max_projector_residual']:.2e}")
    print(f"  Within Band:        {res['audit']['within_spectral_band']}")
