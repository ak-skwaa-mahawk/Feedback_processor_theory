import numpy as np
from math import pi, exp
from typing import Dict, List, Tuple

GROUND_STATE = 0.1    # Baseline phase
DIFFERENCE = 0.05     # Phase deviation
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal: np.ndarray, damp_factor: float = 0.5) -> np.ndarray:
    """Apply exponential damping to signal, reflecting cosmic harmony."""
    return signal * np.exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(time_phase: float) -> Dict[str, float]:
    """Cyclic weighting for T/I/F with Inuit reciprocity."""
    scale = 0.1
    return {
        "T": 0.5 + scale * np.sin(2 * pi * time_phase),  # Alignment with cosmos
        "I": 0.3 - scale * np.cos(2 * pi * time_phase),  # Reciprocity pause
        "F": 0.2 + scale * np.sin(pi * time_phase)       # Balance check
    }

def phase_lock_recursive(phase_history: List[float]) -> Tuple[float, float]:
    """Recursive phase locking with adaptive damping."""
    if not phase_history:
        return 0.0, 0.0
    locked = 0.0
    alpha = 0.7
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history) if len(phase_history) > 1 else 0.0
    damp_factor = 0.5 + 0.2 * std_dev
    return locked % (2 * pi), min(0.7, max(0.3, damp_factor))

# For backward compatibility with full π/φ + Quetzalcoatl layers (import from previous versions)
# trinity = TrinityHarmonics()  # singleton from v1.1.0 / Quetzalcoatl builds