import numpy as np
from living_zero_core import OwnershipProjector, OwnershipMemory, CA3Dynamics, normalize

def test_tag_similarity_and_recall():
    N=128; d=64
    O=OwnershipProjector(N=N,d=d,seed=2)
    mem=OwnershipMemory(N=N, ownership_projector=O, eta=1e-2, gamma=2.0)
    rng=np.random.RandomState(2)
    p = normalize(rng.normal(size=(N,)))
    tag="owner:test"
    mem.encode(p, raw_tag=tag)
    cue = normalize(p + 0.5 * rng.normal(size=(N,)))
    rec = mem.recall_iter(cue, steps=20, bias_tag=tag, beta=3.0)
    sim = float(np.dot(normalize(rec), p))
    assert sim > 0.0  # basic sanity: recall moves toward the pattern

def test_memory_band_invariants():
    from living_zero_core import MemoryBand
    band = MemoryBand()
    N, d = 256, 64
    rng = np.random.RandomState(42)
    O = OwnershipProjector(N=N, d=d, seed=42)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)

    p = normalize(rng.normal(size=(N,)))
    mem.encode(p, raw_tag='owner:test')

    noise_dir = normalize(rng.normal(size=(N,)))
    cue = normalize(p + 0.3 * noise_dir)
    res = band.check_state(cue, p, mem.W)

    assert res["in_angular_band"]
    assert res["in_spectral_band"]
    assert res["stable"]
