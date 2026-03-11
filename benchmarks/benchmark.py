#!/usr/bin/env python3
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
from datetime import datetime

# Sovereign stack
from living_zero_core import OwnershipProjector, OwnershipMemory, normalize
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
from encode_living_stone_to_ultrasound import encode_living_stone_to_ultrasound
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver

# === CONFIG ===
HEIR_ID = "John Danzhit Carroll, Doyon #D-456789"
REGISTRY_FILE = "soliton_registry.jsonl"

gtc = GTCSovereignEngine()
observer = MetaObserver()

def capacity_test(N=512, P=50):
    rng = np.random.RandomState(0)
    O = OwnershipProjector(N=N, d=64, seed=0)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)

    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    tags = [f"owner:{i}" for i in range(P)]

    for p, t in zip(patterns, tags):
        mem.encode(p, raw_tag=t)

    # Recall from 50% noise
    results = []
    for idx, p in enumerate(patterns):
        cue = normalize(p + 0.5 * rng.normal(size=(N,)))
        rec = mem.recall_iter(cue, steps=30, bias_tag=tags[idx], beta=3.0)
        sim = float(np.dot(normalize(rec), p))
        results.append(sim)

    mean_sim = sum(results) / len(results)

    # Sovereign receipt
    payload = {
        "test": "capacity_test",
        "N": N,
        "P": P,
        "mean_similarity": round(mean_sim, 4),
        "passes_reclamation": mean_sim >= 0.55,
        "reclamation_context": "GTC-1740259200 • 55.1"
    }
    receipt = Handshake.createReceipt(None, "LIVING-ZERO-CAPACITY", payload)

    # Registry + Fireseed + Observer
    gtc.allocate_fireseed("session-τ-001", 1.0, note="Capacity Benchmark Pass")
    observer.intercept_response(json.dumps(receipt))

    if mean_sim >= 0.55:
        GlyphParser.parseAndProcess(f"CAPACITY-RESONANCE-{round(mean_sim, 3)}", None)
        encode_living_stone_to_ultrasound()

    with open(REGISTRY_FILE, "a") as f:
        f.write(json.dumps({
            "entry_type": "BENCHMARK",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "mean_similarity": round(mean_sim, 4),
            "status": "RECLAIMED" if mean_sim >= 0.55 else "BUILDING",
            "hash": hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        }) + "\n")

    print(f"🔥 Sovereign Receipt stamped: {receipt['payload_hash'][:16]}...")
    return results, mean_sim

if __name__ == "__main__":
    print("🧠 Living Zero Core Capacity Benchmark — Sahneuti-99733-Q sealed")
    res, mean = capacity_test(N=512, P=40)
    print(f"Mean similarity: {mean:.4f}")
    print("Status: RECLAIMED" if mean >= 0.55 else "Building resonance")