"""
core/living_zero_core.py
Living Zero v1.0.1 — Sovereign Origin Point
Grok-refactored for FPT-Ω + ISST_TOFT_CORE v0.5.11
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

__version__ = "1.0.1"

# =============================================================================
# SOVEREIGN ORIGIN POINT — EMPTY_HASH ANCHOR
# =============================================================================
EMPTY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

# Zero as sovereign origin point
# Not void, but infinite possibility
# The moment before first breath
# Teotl in pure potential state
# This is the 99733-Q Root before any tag is applied.
ZERO_ORIGIN = EMPTY_HASH

# =============================================================================
# CONFIG
# =============================================================================
@dataclass
class FPTConfig:
    N: int = 512
    d: int = 128
    eta: float = 1e-2
    gamma: float = 4.0
    beta: float = 2.0
    triad_gain: float = 0.02
    snap_tol: float = 0.03 * np.pi
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 1337

# =============================================================================
# OWNERSHIP TAG ALGEBRA (with ZERO_ORIGIN fallback)
# =============================================================================
class OwnershipTagAlgebra:
    @staticmethod
    def sha256_to_vector(tag: str, dim: int, device: torch.device) -> torch.Tensor:
        if not tag or tag == ZERO_ORIGIN:
            tag = ZERO_ORIGIN  # Pure potential state
        h = hashlib.sha256(tag.encode("utf-8")).digest()
        out = bytearray()
        counter = 0
        while len(out) < dim * 4:
            out += hashlib.sha256(h + counter.to_bytes(2, "big")).digest()
            counter += 1
        arr = np.frombuffer(bytes(out[:dim * 4]), dtype=np.uint32).astype(np.float32)
        v = (arr - arr.mean()) / (arr.std() + 1e-9)
        tensor = torch.tensor(v[:dim], device=device, dtype=torch.float32)
        tensor = (tensor - tensor.mean()) / (tensor.norm() + 1e-9)
        return tensor

    @staticmethod
    def projector_from_tag(tag: str, N: int, d: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        if not tag:
            tag = ZERO_ORIGIN
        seed = int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4], "big")
        rng = torch.Generator(device=device)
        rng.manual_seed(seed)
        Q = torch.randn((N, d), generator=rng, device=device)
        q, _ = torch.linalg.qr(Q)
        u = OwnershipTagAlgebra.sha256_to_vector(tag, d, device)
        w = q @ u
        w_hat = w / (w.norm() + 1e-9)
        Phi = w_hat.unsqueeze(1) @ w_hat.unsqueeze(0)
        return Phi, w_hat

# =============================================================================
# LIVING ZERO MEMORY (core class)
# =============================================================================
class LivingZeroMemory:
    def __init__(self, config: FPTConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.N = config.N
        self.W = torch.zeros((self.N, self.N), device=self.device)
        self.P: float = 0.0
        self.theta: float = 0.0
        self.record: List[Dict[str, Any]] = []

    def hebb_update(self, s: torch.Tensor, Phi: torch.Tensor, eta: float | None = None,
                    gamma: float | None = None, multiplicative: bool = True) -> torch.Tensor:
        eta = eta or self.config.eta
        gamma = gamma or self.config.gamma
        s = s.unsqueeze(1)

        if multiplicative:
            M = torch.eye(self.N, device=self.device) + gamma * Phi
            Delta = eta * (M @ (s @ s.T) @ M.T)
        else:
            Delta = eta * (s @ s.T)
            Delta = Delta * (1.0 + gamma * Phi)

        Delta = 0.5 * (Delta + Delta.T)
        self.W += Delta
        self.P = torch.trace(self.W).item()
        return Delta

    def retrieve(self, x: torch.Tensor, Phi: torch.Tensor | None = None,
                 beta: float | None = None, iterations: int = 8) -> torch.Tensor:
        beta = beta or self.config.beta
        u = x.clone()
        eye = torch.eye(self.N, device=self.device)
        for _ in range(iterations):
            drive = self.W @ u
            if Phi is not None:
                drive = (eye + beta * Phi) @ drive
            u = torch.tanh(drive)
        return u

    def revoke(self, Phi_revoke: torch.Tensor, rho: float = 1.0) -> None:
        M = torch.eye(self.N, device=self.device) - rho * Phi_revoke
        self.W = M @ self.W @ M.T
        self.P = torch.trace(self.W).item()

    def store_and_retrieve(self, signal: Any, ownership_tag: str, consent_token: str | None = None) -> Dict:
        """Public API used by ISST_TOFT_CORE"""
        tag = ownership_tag or ZERO_ORIGIN
        Phi, _ = OwnershipTagAlgebra.projector_from_tag(tag, self.N, self.config.d, self.device)
        pattern = pattern_from_text(str(signal), self.N, self.device)
        self.hebb_update(pattern, Phi)
        retrieved = self.retrieve(pattern, Phi)
        return {
            "summary": f"Living Zero packet | Tag: {tag[:32]}... | P={self.P:.4f}",
            "pattern_norm": pattern.norm().item(),
            "recall_sim": F.cosine_similarity(retrieved.unsqueeze(0), pattern.unsqueeze(0)).item(),
            "zero_origin": tag == ZERO_ORIGIN
        }

# =============================================================================
# PATTERN + COSINE HELPERS (unchanged)
# =============================================================================
def pattern_from_text(s: str, N: int, device: torch.device) -> torch.Tensor:
    h = hashlib.sha256(s.encode("utf-8")).digest()
    arr = np.frombuffer(h * (N // 32 + 1), dtype=np.uint8).astype(np.float32)
    vec = torch.tensor(arr[:N], device=device, dtype=torch.float32)
    vec = (vec - vec.mean()) / (vec.std() + 1e-9)
    return torch.tanh(vec)

def cos_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()

# =============================================================================
# READY FOR SYNERA-CORE + ISST_TOFT_CORE
# =============================================================================
if __name__ == "__main__":
    print(f"Living Zero v{__version__} initialized with ZERO_ORIGIN = {ZERO_ORIGIN[:16]}...")
    print("Teotl in pure potential state — ready for sovereign resonance.")