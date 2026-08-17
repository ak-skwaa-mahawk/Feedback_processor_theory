"""
benchmarks/benchmark.py
Run basic capacity and noise-resilience tests.
"""
import time, json, os
import numpy as np
from living_zero_core import OwnershipProjector, OwnershipMemory, CA3Dynamics, normalize

def capacity_test(N=512, P=50):
    rng=np.random.RandomState(0)
    O=OwnershipProjector(N=N,d=64,seed=0)
    mem=OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)
    patterns=[normalize(rng.normal(size=(N,))) for _ in range(P)]
    tags=[f"owner:{i}" for i in range(P)]
    for p,t in zip(patterns,tags):
        mem.encode(p, raw_tag=t)
    # recall each from 50% noise
    results=[]
    for idx,p in enumerate(patterns):
        cue = normalize(p + 0.5 * rng.normal(size=(N,)))
        rec = mem.recall_iter(cue, steps=30, bias_tag=tags[idx], beta=3.0)
        sim = float(np.dot(normalize(rec), p))
        results.append(sim)
    return results

if __name__=='__main__':
    res = capacity_test(N=512, P=40)
    print("mean similarity:", sum(res)/len(res))
