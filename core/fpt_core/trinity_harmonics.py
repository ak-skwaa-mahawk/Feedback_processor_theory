# fpt_core/trinity_harmonics.py
import numpy as np
from math import pi, exp

GROUND_STATE, DIFFERENCE = 0.1, 0.05
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}

def trinity_damping(signal, damp_factor): return signal * exp(-damp_factor * np.arange(len(signal)))
def dynamic_weights(t): return {"T": 0.5 + 0.1 * np.sin(2 * pi * t), "I": 0.3 - 0.1 * np.cos(2 * pi * t), "F": 0.2 + 0.1 * np.sin(pi * t)}
def phase_lock_recursive(phases): return (sum(0.7 * p + 0.3 * locked for p in phases) % (2 * pi), 0.5 + 0.2 * np.std(phases))