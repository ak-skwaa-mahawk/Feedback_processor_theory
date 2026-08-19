"""
living_zero_diagnostics.py
Mathematical auditing and invariant verification suite for Ownership Dynamics.
"""
from __future__ import annotations
import numpy as np
from living_zero_core import OwnershipEncoder, OwnershipMemory, MemoryBand

def audit_memory_state(mem: OwnershipMemory, tags: list[str], band: MemoryBand) -> dict:
    """Audits mathematical invariants across the current memory state."""
    # 1. Check weight matrix symmetry and spectral radius
    sym_error = float(np.linalg.norm(mem.W - mem.W.T))
    eigvals = np.linalg.eigvals(mem.W)
    spectral_radius = float(np.max(np.abs(eigvals)))

    # 2. Check tag projector orthogonality and idempotence
    enc = OwnershipEncoder(d=mem.Oproj.d)
    projector_residuals = []
    for tag in tags:
        u = enc.encode(tag)
        Phi, _ = mem.Oproj.projector(u)
        res = float(np.linalg.norm(Phi @ Phi - Phi))
        projector_residuals.append(res)

    return {
        "sym_error": sym_error,
        "spectral_radius": spectral_radius,
        "max_projector_residual": max(projector_residuals) if projector_residuals else 0.0,
        "within_spectral_band": band.spectral_min <= spectral_radius <= band.spectral_max,
    }
