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

def test_mathematical_invariants():
    from living_zero_core import OwnershipProjector, OwnershipMemory, MemoryBand, OwnershipEncoder, normalize
    N, d = 128, 32
    O = OwnershipProjector(N=N, d=d, seed=7)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=1e-3, gamma=1.0)
    band = MemoryBand()
    enc = OwnershipEncoder(d=d)

    # 1. Projector Idempotence & Symmetry: Phi^2 == Phi, Phi == Phi^T
    u = enc.encode("owner:invariants")
    Phi, w_hat = O.projector(u)
    assert np.allclose(Phi @ Phi, Phi, atol=1e-10)
    assert np.allclose(Phi, Phi.T, atol=1e-10)
    assert np.isclose(np.linalg.norm(w_hat), 1.0, atol=1e-10)

    # 2. Weight Matrix Symmetry
    rng = np.random.RandomState(7)
    p = normalize(rng.normal(size=(N,)))
    mem.encode(p, raw_tag="owner:invariants")
    assert np.allclose(mem.W, mem.W.T, atol=1e-10)

def test_mathematical_invariants():
    from living_zero_core import OwnershipProjector, OwnershipMemory, MemoryBand, OwnershipEncoder, normalize
    N, d = 128, 32
    O = OwnershipProjector(N=N, d=d, seed=7)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=1e-3, gamma=1.0)
    band = MemoryBand()
    enc = OwnershipEncoder(d=d)
    u = enc.encode("owner:invariants")
    Phi, w_hat = O.projector(u)
    assert np.allclose(Phi @ Phi, Phi, atol=1e-10)
    assert np.allclose(Phi, Phi.T, atol=1e-10)
    assert np.isclose(np.linalg.norm(w_hat), 1.0, atol=1e-10)
    p = normalize(np.random.RandomState(7).normal(size=(N,)))
    mem.encode(p, raw_tag="owner:invariants")
    assert np.allclose(mem.W, mem.W.T, atol=1e-10)

def test_audit_memory_state_report():
    from living_zero_core import OwnershipProjector, OwnershipMemory, MemoryBand, normalize
    from living_zero_diagnostics import audit_memory_state
    N, d = 128, 32
    O = OwnershipProjector(N=N, d=d, seed=12)
    mem = OwnershipMemory(N=N, ownership_projector=O, eta=5e-3, gamma=1.0)
    band = MemoryBand()
    p = normalize(np.random.RandomState(12).normal(size=(N,)))
    mem.encode(p, raw_tag="owner:audit")
    report = audit_memory_state(mem, ["owner:audit"], band)
    assert report["sym_error"] < 1e-12
    assert report["max_projector_residual"] < 1e-12
    assert report["within_spectral_band"]

def test_projection_rule_continuous_capacity():
    from living_zero_core import normalize, MemoryBand
    N, P = 256, 30
    rng = np.random.RandomState(42)
    band = MemoryBand()

    X = np.array([normalize(rng.normal(size=(N,))) for _ in range(P)])
    W = X.T @ np.linalg.pinv(X @ X.T) @ X

    for p in X:
        cue = normalize(p + 0.3 * normalize(rng.normal(size=(N,))))
        rec = normalize(W @ cue)
        assert float(np.dot(rec, p)) > 0.95
        status = band.check_state(rec, p, W)
        assert status["in_angular_band"]

def test_online_projection_memory():
    from living_zero_core import OwnershipProjector, normalize, MemoryBand
    from living_zero_projection import OnlineProjectionMemory
    N, d, P = 256, 32, 20
    rng = np.random.RandomState(99)
    O = OwnershipProjector(N=N, d=d, seed=99)
    mem = OnlineProjectionMemory(N=N, ownership_projector=O)
    band = MemoryBand()

    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    for i, p in enumerate(patterns):
        mem.encode(p, raw_tag=f"owner:{i}")

    # Verify projector idempotence and symmetry
    assert np.allclose(mem.P_mat @ mem.P_mat, mem.P_mat, atol=1e-10)
    assert np.allclose(mem.P_mat, mem.P_mat.T, atol=1e-10)

    for i, p in enumerate(patterns):
        cue = normalize(p + 0.3 * normalize(rng.normal(size=(N,))))
        rec = mem.recall(cue, bias_tag=f"owner:{i}", beta=0.5)
        sim = float(np.dot(rec, p))
        assert sim > 0.95
        assert band.check_state(rec, p, mem.P_mat)["in_angular_band"]

def test_online_projection_revocation():
    from living_zero_core import OwnershipProjector, normalize
    from living_zero_projection import OnlineProjectionMemory
    N, d = 256, 32
    rng = np.random.RandomState(101)
    O = OwnershipProjector(N=N, d=d, seed=101)
    mem = OnlineProjectionMemory(N=N, ownership_projector=O)

    p0 = normalize(rng.normal(size=(N,)))
    p1 = normalize(rng.normal(size=(N,)))
    mem.encode(p0, raw_tag="owner:alice")
    mem.encode(p1, raw_tag="owner:bob")

    # Add selective revocation method to OnlineProjectionMemory if not present
    # Revoke alice's pattern subspace: P <- (I - p0 p0^T) P (I - p0 p0^T)
    P_alice = np.outer(p0, p0)
    mem.P_mat = (np.eye(N) - P_alice) @ mem.P_mat @ (np.eye(N) - P_alice)
    mem.P_mat = 0.5 * (mem.P_mat + mem.P_mat.T)

    rec0 = mem.recall(p0)
    rec1 = mem.recall(p1)

    assert float(np.dot(rec0, p0)) < 0.1
    assert float(np.dot(rec1, p1)) > 0.95

def test_online_projection_revocation():
    from living_zero_core import OwnershipProjector, normalize
    from living_zero_projection import OnlineProjectionMemory
    N, d = 256, 32
    rng = np.random.RandomState(101)
    O = OwnershipProjector(N=N, d=d, seed=101)
    mem = OnlineProjectionMemory(N=N, ownership_projector=O)

    p0 = normalize(rng.normal(size=(N,)))
    p1 = normalize(rng.normal(size=(N,)))
    mem.encode(p0, raw_tag="owner:alice")
    mem.encode(p1, raw_tag="owner:bob")

    mem.selective_revoke("owner:alice")

    rec0 = mem.recall(p0)
    rec1 = mem.recall(p1)

    assert float(np.dot(rec0, p0)) < 0.1
    assert float(np.dot(rec1, p1)) > 0.95
