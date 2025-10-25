# fpt_core/trinity_harmonics.py
import numpy as np
from math import pi, exp

GROUND_STATE = 0.1    # Baseline phase
DIFFERENCE = 0.05     # Phase deviation
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal, damp_factor):
    """Apply exponential damping to signal, reflecting cosmic harmony."""
    return signal * exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(time_phase):
    """Cyclic weighting for T/I/F with Inuit reciprocity."""
    scale = 0.1
    return {
        "T": 0.5 + scale * np.sin(2 * pi * time_phase),  # Alignment with cosmos
        "I": 0.3 - scale * np.cos(2 * pi * time_phase),  # Reciprocity pause
        "F": 0.2 + scale * np.sin(pi * time_phase)       # Balance check
    }

def phase_lock_recursive(phase_history):
    """Recursive phase locking with adaptive damping."""
    locked = 0.0
    alpha = 0.7  # Fixed smoothing factor
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history)
    damp_factor = 0.5 + 0.2 * std_dev  # Linear adjustment
    return locked % (2 * pi), min(0.7, max(0.3, damp_factor))