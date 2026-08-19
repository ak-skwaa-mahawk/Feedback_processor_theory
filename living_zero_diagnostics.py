from __future__ import annotations
import numpy as np
from living_zero_core import OwnershipEncoder, OwnershipMemory, MemoryBand

def audit_memory_state(mem: OwnershipMemory, tags: list[str], band: MemoryBand) -> dict:
    sym_error = float(np.linalg.norm(mem.W - mem.W.T))
    spectral_radius = float(np.max(np.abs(np.linalg.eigvals(mem.W))))
    enc = OwnershipEncoder(d=mem.Oproj.d)
    projector_residuals = [float(np.linalg.norm((lambda P: P @ P - P)(mem.Oproj.projector(enc.encode(t))[0]))) for t in tags]
    return {
        "sym_error": sym_error,
        "spectral_radius": spectral_radius,
        "max_projector_residual": max(projector_residuals) if projector_residuals else 0.0,
        "within_spectral_band": band.spectral_min <= spectral_radius <= band.spectral_max,
    }
