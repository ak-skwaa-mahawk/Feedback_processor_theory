from __future__ import annotations
import numpy as np
from living_zero_core import normalize, OwnershipEncoder, OwnershipProjector

class OnlineProjectionMemory:
    def __init__(self, N: int, ownership_projector: OwnershipProjector):
        self.N = N
        self.Oproj = ownership_projector
        self.P_mat = np.zeros((N, N), dtype=float)
        self.tags: dict[str, np.ndarray] = {}

    def encode(self, s: np.ndarray, raw_tag: str | None = None) -> None:
        v = normalize(np.array(s, dtype=float))
        if np.linalg.norm(self.P_mat) == 0:
            self.P_mat = np.outer(v, v)
        else:
            v_perp = v - self.P_mat @ v
            norm_sq = float(np.dot(v_perp, v_perp))
            if norm_sq > 1e-8:
                q = v_perp / np.sqrt(norm_sq)
                self.P_mat += np.outer(q, q)
                self.P_mat = 0.5 * (self.P_mat + self.P_mat.T)
        if raw_tag is not None:
            self.tags[raw_tag] = v

    def selective_revoke(self, raw_tag: str) -> None:
        if raw_tag in self.tags:
            v = self.tags[raw_tag]
            P_v = np.outer(v, v)
            self.P_mat = (np.eye(self.N) - P_v) @ self.P_mat @ (np.eye(self.N) - P_v)
            self.P_mat = 0.5 * (self.P_mat + self.P_mat.T)
            del self.tags[raw_tag]

    def recall(self, cue: np.ndarray, bias_tag: str | None = None, beta: float = 0.0) -> np.ndarray:
        x = np.array(cue, dtype=float)
        rec = self.P_mat @ x
        if bias_tag is not None and beta != 0.0:
            enc = OwnershipEncoder(d=self.Oproj.d)
            u = enc.encode(bias_tag)
            Phi, _ = self.Oproj.projector(u)
            rec = (np.eye(self.N) + beta * Phi) @ rec
        norm = np.linalg.norm(rec)
        if norm < 0.5:
            return np.zeros_like(rec)
        return rec / norm
