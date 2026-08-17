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
