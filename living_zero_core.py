"""
living_zero_core.py
Core implementation: Ownership Tag Algebra + CA3 dynamics
Lightweight, single-file module ready for import and local development.
"""

from __future__ import annotations
import math, hashlib, time
from typing import Dict, Optional
import numpy as np

# ---------- Utilities ----------
def normalize(v, eps=1e-12):
    v = np.array(v, dtype=float)
    n = np.linalg.norm(v)
    if n < eps:
        return v
    return v / n

# ---------- Ownership Encoder & Projector ----------
class OwnershipEncoder:
    def __init__(self, d: int = 64):
        self.d = int(d)
    def _seed_from_raw(self, raw) -> int:
        s = str(raw).encode('utf-8')
        h = hashlib.md5(s).hexdigest()
        return int(h[:8], 16) % (2**31 - 1)
    def encode(self, raw) -> np.ndarray:
        seed = self._seed_from_raw(raw)
        rng = np.random.RandomState(seed)
        v = rng.normal(size=(self.d,))
        return normalize(v)

class OwnershipProjector:
    def __init__(self, N:int, d:int=64, seed:int=0):
        self.N = int(N); self.d = int(d)
        rng = np.random.RandomState(seed)
        Q_random = rng.normal(size=(self.N, self.d))
        if self.N >= self.d:
            Q_mat, _ = np.linalg.qr(Q_random, mode='reduced')
        else:
            U, _, _ = np.linalg.svd(Q_random, full_matrices=False)
            Q_mat = U[:, :self.d]
        self.Q = Q_mat[:, :self.d]
    def projector(self, ownership_vector:np.ndarray):
        w = self.Q @ ownership_vector
        w_hat = normalize(w)
        Phi = np.outer(w_hat, w_hat)
        return Phi, w_hat

# ---------- Ownership-aware associative memory ----------
class OwnershipMemory:
    def __init__(self, N:int, ownership_projector:OwnershipProjector, eta=1e-3, gamma=1.0, weight_decay=0.0):
        self.N = int(N)
        self.Oproj = ownership_projector
        self.W = np.zeros((self.N, self.N), dtype=float)
        self.eta = float(eta); self.gamma = float(gamma); self.weight_decay = float(weight_decay)
    def standard_hebb(self, s):
        return self.eta * np.outer(s, s)
    def ownership_hebb_multiplicative(self, s, raw_tag):
        enc = OwnershipEncoder(d=self.Oproj.d)
        u = enc.encode(raw_tag)
        Phi, _ = self.Oproj.projector(u)
        M = np.eye(self.N) + self.gamma * Phi
        Delta = M @ (np.outer(s, s) * self.eta) @ M.T
        return Delta
    def encode(self, s, raw_tag=None):
        s = np.array(s, dtype=float)
        if raw_tag is None:
            Delta = self.standard_hebb(s)
        else:
            Delta = self.ownership_hebb_multiplicative(s, raw_tag)
        self.W += Delta
        if self.weight_decay > 0:
            self.W *= (1.0 - self.weight_decay)
        self.W = 0.5 * (self.W + self.W.T)
    def recall_iter(self, x0, steps=10, bias_tag=None, beta=0.0, activation=np.tanh):
        x = np.array(x0, dtype=float)
        Phi = None
        if bias_tag is not None:
            enc = OwnershipEncoder(d=self.Oproj.d)
            u = enc.encode(bias_tag)
            Phi, _ = self.Oproj.projector(u)
        for _ in range(steps):
            u = self.W @ x
            if Phi is not None and beta != 0.0:
                u = (np.eye(self.N) + beta * Phi) @ u
            x = activation(u)
        return x
    def selective_revoke(self, raw_tag, rho=1.0):
        enc = OwnershipEncoder(d=self.Oproj.d)
        u = enc.encode(raw_tag)
        Phi, _ = self.Oproj.projector(u)
        M = np.eye(self.N) - rho * Phi
        self.W = M @ self.W @ M.T
        self.W = 0.5 * (self.W + self.W.T)
    def tag_similarity(self, raw_tag1, raw_tag2):
        enc = OwnershipEncoder(d=self.Oproj.d)
        u1 = enc.encode(raw_tag1); u2 = enc.encode(raw_tag2)
        Phi1, w1 = self.Oproj.projector(u1); Phi2, w2 = self.Oproj.projector(u2)
        sim = (float(np.dot(w1, w2)))**2
        return float(sim)

# ---------- CA3 Dynamics & Living Zero ----------
class CA3Dynamics:
    def __init__(self, N:int, memory:OwnershipMemory, tau=0.1, dt=0.01):
        self.N = int(N); self.memory = memory; self.tau=float(tau); self.dt=float(dt)
        self.A = np.eye(self.N)
        self.alpha:Dict[int,float] = {}
        self.patterns:Dict[int, np.ndarray] = {}
        self.P = 0.0
    def energy_grad(self, x):
        x = np.array(x, dtype=float)
        grad = self.A @ x
        for mu, alpha_mu in self.alpha.items():
            p = self.patterns[mu]
            proj = np.dot(p, x)
            grad -= alpha_mu * proj * p
        return grad
    def step(self, x, Vd=1.0, R=1.0, b=None, noise_std=0.0):
        g = float(Vd) * float(R)
        gradE = self.energy_grad(x)
        drive = self.memory.W @ x if b is None else self.memory.W @ x + b
        drive = np.tanh(drive)
        eta = np.random.randn(self.N) * noise_std if noise_std > 0 else np.zeros(self.N)
        dx = (-gradE + g * drive + eta) * (self.dt / self.tau)
        return x + dx
    def encode_pattern(self, pid:int, p_vec, strength=0.1):
        self.patterns[pid] = normalize(p_vec); self.alpha[pid]=float(strength)
    def reward_handshake(self, x, target_pid:int, eps=0.03*math.pi, R0=1.0, kappa_r=1e-2, kappa_P=1e-2):
        p = self.patterns[target_pid]
        x_hat = normalize(x); p_hat = normalize(p)
        dot = max(-1.0, min(1.0, float(np.dot(x_hat, p_hat))))
        theta = math.acos(dot)
        if theta <= eps:
            r = R0 * math.exp(-theta/eps)
            self.alpha[target_pid] += kappa_r * r
            self.P += kappa_P * r
            return True, theta, r
        return False, theta, 0.0

# ---------- Convenience: small demo function ----------
def demo_small_run(seed=0):
    rng = np.random.RandomState(seed)
    N = 256; d = 64
    Oproj = OwnershipProjector(N=N, d=d, seed=1)
    mem = OwnershipMemory(N=N, ownership_projector=Oproj, eta=5e-3, gamma=1.5)
    ca3 = CA3Dynamics(N=N, memory=mem)
    # produce patterns and encode
    p = normalize(rng.normal(size=(N,))); tag = "owner:collective"
    mem.encode(p, raw_tag=tag); ca3.encode_pattern(0, p, strength=0.05)
    x = normalize(p + 0.8 * rng.normal(size=(N,)))
    events = 0
    for t in range(400):
        x = ca3.step(x, Vd=1.0, R=1.0, noise_std=0.01)
        trig, theta, r = ca3.reward_handshake(x, 0)
        if trig:
            events += 1
            mem.encode(x, raw_tag=tag)
    return {"final_sim": float(np.dot(normalize(x), normalize(p))), "events": events}


#!/usr/bin/env python3
# living_zero_core.py
"""
Living Zero — Core (Hybrid Functional + Safe)
Single-file module implementing:
 - Ownership Tag Algebra (hash->embedding, projector operators)
 - Ownership-aware associative memory (multiplicative Hebb)
 - CA3-style attractor dynamics with Living-Zero (0.03π handshake)
 - Optional PyTorch GPU acceleration (if torch installed)
 - Safe training loop, plotting utilities, and small demo
 - No networking, no keys, no autonomous actions

Usage (quick):
    python -c "from living_zero_core import demo_small; demo_small()"

Notes:
 - This module intentionally keeps all heavy runs gated behind functions.
 - For full GPU runs, install PyTorch (with CUDA) separately.
 - Keep this file offline / local if you prefer — it's ready to run locally.
"""

from __future__ import annotations
import math
import hashlib
import json
import os
import time
from typing import Dict, Optional, Tuple, List

import numpy as np

# Try optional imports (matplotlib, torch). None are required for basic operation.
_HAS_MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    _HAS_MATPLOTLIB = True
except Exception:
    _HAS_MATPLOTLIB = False

_HAS_TORCH = False
try:
    import torch
    import torch.nn.functional as F
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False

# ---------------------------
# Utilities
# ---------------------------
def normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    arr = np.asarray(v, dtype=float)
    n = np.linalg.norm(arr)
    if n < eps:
        return arr
    return arr / n

def ensure_ndarray(x) -> np.ndarray:
    return np.asarray(x, dtype=float)

# ---------------------------
# Ownership Tag Algebra (Hybrid)
# ---------------------------
class OwnershipEncoder:
    """
    Deterministic, reproducible mapping from a raw tag (string) to a d-dim vector.
    Uses MD5 to seed a RNG for portability. For cryptographic needs, replace
    with a HMAC or crypto-safe derivation outside of this file.
    """
    def __init__(self, d: int = 64):
        self.d = int(d)

    def _seed_from_raw(self, raw: str) -> int:
        s = str(raw).encode("utf-8")
        h = hashlib.md5(s).hexdigest()
        # use first 8 hex chars (32-bit) as seed
        return int(h[:8], 16) % (2**31 - 1)

    def encode(self, raw: str) -> np.ndarray:
        seed = self._seed_from_raw(raw)
        rng = np.random.RandomState(seed)
        v = rng.normal(size=(self.d,))
        return normalize(v)

class OwnershipProjector:
    """
    Project ownership vector (d-dim) into pattern space (N-dim) via a random orthogonal projection Q.
    Returns rank-1 projector Phi = w_hat w_hat^T and the projected vector w_hat.
    """
    def __init__(self, N: int, d: int = 64, seed: int = 0):
        self.N = int(N)
        self.d = int(d)
        rng = np.random.RandomState(seed)
        Q_random = rng.normal(size=(self.N, self.d))
        if self.N >= self.d:
            # thin QR
            Q_mat, _ = np.linalg.qr(Q_random, mode="reduced")
        else:
            U, _, _ = np.linalg.svd(Q_random, full_matrices=False)
            Q_mat = U[:, :self.d]
        self.Q = Q_mat[:, :self.d]

    def projector(self, ownership_vector: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        w = self.Q @ ownership_vector
        w_hat = normalize(w)
        Phi = np.outer(w_hat, w_hat)
        return Phi, w_hat

# ---------------------------
# Ownership-aware associative memory
# ---------------------------
class OwnershipMemory:
    """
    Symmetric associative memory W (NxN) with multiplicative ownership modulation.
    Methods:
      - encode(s, tag) : ownership-aware multiplicative Hebb
      - recall_iter(cue, steps, bias_tag, beta) : iterative attractor recall with optional ownership bias
      - selective_revoke(tag, rho) : soft/hard revoke in the ownership subspace
      - tag_similarity(a,b)
    """
    def __init__(self, N: int, ownership_projector: OwnershipProjector, eta: float = 1e-3, gamma: float = 1.0, weight_decay: float = 0.0):
        self.N = int(N)
        self.Oproj = ownership_projector
        self.W = np.zeros((self.N, self.N), dtype=float)
        self.eta = float(eta)
        self.gamma = float(gamma)
        self.weight_decay = float(weight_decay)
        # small numerical stability clamp for symmetric ops
        self._sym_clamp_eps = 1e-15

    def standard_hebb(self, s: np.ndarray) -> np.ndarray:
        s = ensure_ndarray(s)
        return self.eta * np.outer(s, s)

    def ownership_hebb_multiplicative(self, s: np.ndarray, raw_tag: str) -> np.ndarray:
        s = ensure_ndarray(s)
        enc = OwnershipEncoder(d=self.Oproj.d)
        u = enc.encode(raw_tag)
        Phi, _ = self.Oproj.projector(u)
        M = np.eye(self.N) + self.gamma * Phi
        # multiplicative: preserves PSD (if initial W is PSD)
        Delta = M @ (np.outer(s, s) * self.eta) @ M.T
        return Delta

    def encode(self, s: np.ndarray, raw_tag: Optional[str] = None) -> None:
        if raw_tag is None:
            Delta = self.standard_hebb(s)
        else:
            Delta = self.ownership_hebb_multiplicative(s, raw_tag)
        self.W += Delta
        if self.weight_decay > 0:
            self.W *= (1.0 - self.weight_decay)
        # symmetrize numerically
        self.W = 0.5 * (self.W + self.W.T) + self._sym_clamp_eps * np.eye(self.N)

    def recall_iter(self, x0: np.ndarray, steps: int = 10, bias_tag: Optional[str] = None, beta: float = 0.0, activation=np.tanh) -> np.ndarray:
        x = ensure_ndarray(x0).astype(float)
        Phi = None
        if bias_tag is not None:
            enc = OwnershipEncoder(d=self.Oproj.d)
            u = enc.encode(bias_tag)
            Phi, _ = self.Oproj.projector(u)
        for _ in range(steps):
            u = self.W @ x
            if Phi is not None and beta != 0.0:
                u = (np.eye(self.N) + beta * Phi) @ u
            x = activation(u)
        return x

    def selective_revoke(self, raw_tag: str, rho: float = 1.0) -> None:
        enc = OwnershipEncoder(d=self.Oproj.d)
        u = enc.encode(raw_tag)
        Phi, _ = self.Oproj.projector(u)
        M = np.eye(self.N) - rho * Phi
        self.W = M @ self.W @ M.T
        self.W = 0.5 * (self.W + self.W.T)

    def tag_similarity(self, raw_tag1: str, raw_tag2: str) -> float:
        enc = OwnershipEncoder(d=self.Oproj.d)
        u1 = enc.encode(raw_tag1)
        u2 = enc.encode(raw_tag2)
        Phi1, w1 = self.Oproj.projector(u1)
        Phi2, w2 = self.Oproj.projector(u2)
        # For rank-1 projectors, tr(Phi1 Phi2) = (w1^T w2)^2
        sim = float(np.dot(w1, w2)) ** 2
        return float(sim)

    def save(self, path: str) -> None:
        np.savez_compressed(path, W=self.W)

    def load(self, path: str) -> None:
        data = np.load(path)
        self.W = data["W"]

# ---------------------------
# CA3-style dynamics (Living Zero)
# ---------------------------
class CA3Dynamics:
    """
    Encodes:
      - Energy landscape with living-zero at x=0 and negative wells for stored patterns
      - Discrete-time integration combining energy descent and associative drive
      - Reward handshake at angular tolerance eps = 0.03 * pi
    """
    def __init__(self, N: int, memory: OwnershipMemory, tau: float = 0.1, dt: float = 0.01):
        self.N = int(N)
        self.memory = memory
        self.tau = float(tau)
        self.dt = float(dt)
        self.A = np.eye(self.N)  # curvature at living-zero
        self.alpha: Dict[int, float] = {}
        self.patterns: Dict[int, np.ndarray] = {}
        self.P = 0.0  # long-term stored potential

    def energy_grad(self, x: np.ndarray) -> np.ndarray:
        x = ensure_ndarray(x)
        grad = self.A @ x
        for mu, alpha_mu in self.alpha.items():
            p = self.patterns[mu]
            proj = float(np.dot(p, x))
            grad -= alpha_mu * proj * p
        return grad

    def step(self, x: np.ndarray, Vd: float = 1.0, R: float = 1.0, b: Optional[np.ndarray] = None, noise_std: float = 0.0) -> np.ndarray:
        g = float(Vd) * float(R)
        gradE = self.energy_grad(x)
        drive = (self.memory.W @ x) if b is None else (self.memory.W @ x + b)
        drive = np.tanh(drive)
        eta = np.random.randn(self.N) * noise_std if noise_std > 0 else np.zeros(self.N)
        dx = (-gradE + g * drive + eta) * (self.dt / self.tau)
        return x + dx

    def encode_pattern(self, pid: int, p_vec: np.ndarray, strength: float = 0.1) -> None:
        self.patterns[pid] = normalize(p_vec)
        self.alpha[pid] = float(strength)

    def reward_handshake(self, x: np.ndarray, target_pid: int, eps: float = 0.03 * math.pi, R0: float = 1.0, kappa_r: float = 1e-2, kappa_P: float = 1e-2) -> Tuple[bool, float, float]:
        p = self.patterns[target_pid]
        x_hat = normalize(x)
        p_hat = normalize(p)
        dot = max(-1.0, min(1.0, float(np.dot(x_hat, p_hat))))
        theta = math.acos(dot)
        if theta <= eps:
            r = R0 * math.exp(-theta / eps)
            self.alpha[target_pid] += kappa_r * r
            self.P += kappa_P * r
            return True, theta, r
        return False, theta, 0.0

# ---------------------------
# Optional PyTorch wrappers (GPU-ready)
# ---------------------------
if _HAS_TORCH:
    class TorchOwnershipEncoder:
        def __init__(self, d: int = 64, device: Optional[torch.device] = None):
            self.d = int(d)
            self.device = device if device is not None else torch.device("cpu")

        def _seed_from_raw(self, raw: str) -> int:
            s = str(raw).encode("utf-8")
            h = hashlib.md5(s).hexdigest()
            return int(h[:8], 16) % (2**31 - 1)

        def encode(self, raw: str) -> torch.Tensor:
            seed = self._seed_from_raw(raw)
            rng = np.random.RandomState(seed)
            v = rng.normal(size=(self.d,)).astype("float32")
            t = torch.from_numpy(v).to(self.device)
            return t / (t.norm() + 1e-12)

    class TorchOwnershipProjector:
        def __init__(self, N: int, d: int = 64, seed: int = 0, device: Optional[torch.device] = None):
            self.N = int(N)
            self.d = int(d)
            self.device = device if device is not None else torch.device("cpu")
            rng = np.random.RandomState(seed)
            Q_random = rng.normal(size=(self.N, self.d)).astype("float32")
            if self.N >= self.d:
                Q_mat, _ = np.linalg.qr(Q_random, mode="reduced")
            else:
                U, _, _ = np.linalg.svd(Q_random, full_matrices=False)
                Q_mat = U[:, :self.d]
            self.Q = torch.from_numpy(Q_mat[:, :self.d].astype("float32")).to(self.device)

        def projector(self, ownership_vector: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            w = self.Q.matmul(ownership_vector)
            w_hat = w / (w.norm() + 1e-12)
            Phi = torch.ger(w_hat, w_hat)
            return Phi, w_hat

    class TorchOwnershipMemory:
        def __init__(self, N: int, ownership_projector: TorchOwnershipProjector, eta: float = 1e-3, gamma: float = 1.0, device: Optional[torch.device] = None):
            self.N = int(N)
            self.device = device if device is not None else torch.device("cpu")
            self.Oproj = ownership_projector
            self.W = torch.zeros((self.N, self.N), dtype=torch.float32, device=self.device)
            self.eta = float(eta); self.gamma = float(gamma)

        def encode(self, s, raw_tag: Optional[str] = None):
            if not torch.is_tensor(s):
                s = torch.tensor(s, dtype=torch.float32, device=self.device)
            if raw_tag is None:
                Delta = self.eta * torch.ger(s, s)
            else:
                enc = TorchOwnershipEncoder(d=self.Oproj.d, device=self.device)
                u = enc.encode(raw_tag)
                Phi, _ = self.Oproj.projector(u)
                M = torch.eye(self.N, device=self.device) + self.gamma * Phi
                Delta = M.matmul(self.eta * torch.ger(s, s)).matmul(M.T)
            self.W += Delta
            self.W = 0.5 * (self.W + self.W.T)

        def recall_iter(self, x0, steps=10, bias_tag: Optional[str] = None, beta: float = 0.0, activation=torch.tanh):
            if not torch.is_tensor(x0):
                x = torch.tensor(x0, dtype=torch.float32, device=self.device)
            else:
                x = x0.to(self.device)
            Phi = None
            if bias_tag is not None:
                enc = TorchOwnershipEncoder(d=self.Oproj.d, device=self.device)
                u = enc.encode(bias_tag)
                Phi, _ = self.Oproj.projector(u)
            for _ in range(steps):
                u = self.W.matmul(x)
                if Phi is not None and beta != 0.0:
                    u = (torch.eye(self.N, device=self.device) + beta * Phi).matmul(u)
                x = activation(u)
            return x.cpu().numpy()

# ---------------------------
# Training utilities (safe, controllable)
# ---------------------------
def train_simple_numpy(memory: OwnershipMemory, ca3: CA3Dynamics, patterns: List[np.ndarray], tags: List[str], epochs: int = 10, batch_noise: float = 0.5, replay_on_handshake: bool = True, seed: int = 0) -> Dict:
    """
    Simple training loop:
      - Encodes patterns into memory once
      - Runs attractor dynamics from noisy cues and applies reward-based small re-encodes
    Returns a summary dict with final similarities and handshake counts.
    """
    rng = np.random.RandomState(seed)
    # initial encode
    for p, t in zip(patterns, tags):
        memory.encode(p, raw_tag=t)
    for i, p in enumerate(patterns):
        ca3.encode_pattern(i, p, strength=0.05 + 0.01 * i)

    summary = {"handshakes": 0, "final_sims": []}
    # iterate patterns as cues
    for epoch in range(max(1, epochs)):
        for idx, p in enumerate(patterns):
            cue = normalize(p + batch_noise * rng.normal(size=(memory.N,)))
            x = cue.copy()
            for step in range(400):  # step horizon per cue (safe bounded)
                x = ca3.step(x, Vd=1.0, R=1.0, noise_std=0.01)
                trig, theta, r = ca3.reward_handshake(x, target_pid=idx)
                if trig:
                    summary["handshakes"] += 1
                    if replay_on_handshake:
                        # perform a small re-encode with ownership tag
                        memory.encode(x, raw_tag=tags[idx])
                    # break early if desired (we continue here, but could break)
    # final evaluation
    for idx, p in enumerate(patterns):
        cue = normalize(p + batch_noise * rng.normal(size=(memory.N,)))
        rec = memory.recall_iter(cue, steps=30, bias_tag=tags[idx], beta=3.0)
        sim = float(np.dot(normalize(rec), normalize(p)))
        summary["final_sims"].append(sim)
    return summary

# ---------------------------
# Plotting utilities
# ---------------------------
def plot_histogram(vals: List[float], title: str = "Histogram", bins: int = 20, show: bool = True):
    if not _HAS_MATPLOTLIB:
        print("matplotlib not available; skipping plot.")
        return
    plt.figure(figsize=(6, 4))
    plt.hist(vals, bins=bins)
    plt.title(title)
    plt.tight_layout()
    if show:
        plt.show()

def plot_training_trace(trace: List[float], title: str = "Trace", show: bool = True):
    if not _HAS_MATPLOTLIB:
        print("matplotlib not available; skipping plot.")
        return
    plt.figure(figsize=(6, 3))
    plt.plot(trace)
    plt.title(title)
    plt.tight_layout()
    if show:
        plt.show()

# ---------------------------
# Small safe demos and unit-checks
# ---------------------------
def demo_small(seed: int = 0):
    """Run a small demo (fast) to sanity-check environment."""
    rng = np.random.RandomState(seed)
    N = 256
    d = 64
    Oproj = OwnershipProjector(N=N, d=d, seed=7)
    mem = OwnershipMemory(N=N, ownership_projector=Oproj, eta=5e-3, gamma=1.5)
    ca3 = CA3Dynamics(N=N, memory=mem, tau=0.1, dt=0.01)
    # patterns
    P = 4
    patterns = [normalize(rng.normal(size=(N,))) for _ in range(P)]
    tags = [f"owner:{i}" for i in range(P)]
    # train lightly
    summary = train_simple_numpy(mem, ca3, patterns, tags, epochs=1, batch_noise=0.6, replay_on_handshake=True, seed=seed)
    print("Demo summary:", json.dumps(summary, indent=2))
    # plot final sims if matplotlib available
    if _HAS_MATPLOTLIB:
        plot_histogram(summary["final_sims"], title="Final similarities")
    return summary

def unit_test_quick():
    """Quick unit test for sanity: small encode/recall passes."""
    rng = np.random.RandomState(1)
    N = 128; d = 32
    O = OwnershipProjector(N=N, d=d, seed=4)
    M = OwnershipMemory(N=N, ownership_projector=O, eta=1e-2, gamma=2.0)
    p = normalize(rng.normal(size=(N,)))
    tag = "unit:test"
    M.encode(p, raw_tag=tag)
    cue = normalize(p + 0.4 * rng.normal(size=(N,)))
    rec = M.recall_iter(cue, steps=30, bias_tag=tag, beta=3.0)
    sim = float(np.dot(normalize(rec), p))
    print("Unit test similarity:", sim)
    assert sim > 0.0, "Recall failed to move toward target (sanity)."
    print("Unit test passed.")
    return sim

# ---------------------------
# Utilities for hyperparameter sweep (user-run)
# ---------------------------
def sweep_hyperparameters_for_target(N: int = 1024, target_sim: float = 0.99, max_rounds: int = 10):
    """
    NOTE: This is a helper that *prepares* sweeps. Running a full sweep at N=1024 is compute heavy.
    It returns a list of candidate hyperparameter settings to try locally. Use this to guide experiments.
    """
    # candidate grid (conservative)
    etas = [1e-3, 5e-3, 1e-2]
    gammas = [0.5, 1.0, 1.5, 2.0]
    betas = [1.0, 3.0, 5.0]
    configs = []
    for eta in etas:
        for gamma in gammas:
            for beta in betas:
                configs.append({"N": N, "eta": eta, "gamma": gamma, "beta": beta})
                if len(configs) >= max_rounds:
                    return configs
    return configs

# ---------------------------
# Safety and usage helper
# ---------------------------
def safety_notice():
    print("SAFETY NOTICE:")
    print("- This module is research code; it is not an autonomous agent.")
    print("- No networking, no external control, no secrets embedded.")
    print("- Heavy training runs are gated behind explicit function calls.")
    print("- You are responsible for compliance and ethical deployment.")

# ---------------------------
# CLI / if-run
# ---------------------------
if __name__ == "__main__":
    safety_notice()
    print("Running quick unit test and demo (fast).")
    try:
        s = unit_test_quick()
    except AssertionError as e:
        print("Unit test assertion:", e)
    time.sleep(0.2)
    demo_small()

# End of living_zero_core.py