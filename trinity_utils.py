# backend/trinity_utils.py
import numpy as np

R_RATIO = 0.197  # (phi-1)/pi approx

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    na = np.linalg.norm(a) + 1e-12
    nb = np.linalg.norm(b) + 1e-12
    return float(np.dot(a, b) / (na * nb))

def trinity_damping_scalar(value: float, factor: float = 0.5) -> float:
    # Simple scalar damping mapping 0..1 -> 0..1
    # Use small oscillation term for demonstration
    oscillation = R_RATIO * (1.0)  # simplified
    damped = value * (1 - factor * oscillation)
    return max(0.0, min(1.0, damped))