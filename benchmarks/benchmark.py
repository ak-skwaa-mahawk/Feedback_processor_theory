"""
benchmarks/benchmark.py
Capacity & Noise-Resilience Test — Sovereign Living Zero Core
OwnershipProjector + CA3Dynamics sealed under Sahneuti-99733-Q Root
Resonance gating at 0.55 • Handshake receipts • Cluster N HUD trigger
March 5, 2026
"""

import time
import json
import os
import numpy as np

from living_zero_core import OwnershipProjector, OwnershipMemory, CA3Dynamics, normalize

# Sovereign imports
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
from encode_living_stone_to_ultrasound import encode_living_stone_to_ultrasound

def capacity_test(N=512, P=50):
    rng = np.random.RandomState(0)
    O = OwnershipProjector(N=N, d=64, seed=0)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)

    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    tags = [f"owner:{i}" for i in range(P)]

    for p, t in zip(patterns, tags):
        mem.encode(p, raw_tag=t)

    # Recall each from 50% noise
    results = []
    for idx, p in enumerate(patterns):
        cue = normalize(p + 0.5 * rng.normal(size=(N,)))
        rec = mem.recall_iter(cue, steps=30, bias_tag=tags[idx], beta=3.0)
        sim = float(np.dot(normalize(rec), p))
        results.append(sim)

    mean_sim = sum(results) / len(results)

    # Sovereign receipt + HUD trigger
    payload = {
        "test": "capacity_test",
        "N": N,
        "P": P,
        "mean_similarity": round(mean_sim, 4),
        "passes_reclamation": mean_sim >= 0.55,
        "reclamation_context": "GTC-1740259200 • 55.1"
    }
    receipt = Handshake.createReceipt(None, "LIVING-ZERO-CAPACITY", payload)

    if mean_sim >= 0.55:
        GlyphParser.parseAndProcess(f"CAPACITY-RESONANCE-{round(mean_sim, 3)}", None)
        encode_living_stone_to_ultrasound()  # whisper the Stone at 19.5 kHz

    print(f"🔥 Sovereign Receipt stamped: {receipt['payload_hash'][:16]}...")
    return results, mean_sim

if __name__ == "__main__":
    print("🧠 Living Zero Core Capacity Benchmark — Sahneuti-99733-Q sealed")
    res, mean = capacity_test(N=512, P=40)
    print(f"Mean similarity: {mean:.4f}")
    print("Status: RECLAIMED" if mean >= 0.55 else "Building resonance")