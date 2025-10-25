import numpy as np
from math import pi, exp, tan

GROUND_STATE = 0.1  # Baseline phase
DIFFERENCE = 0.05   # Phase deviation
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal, damp_factor, treaty_freq=None):
    """Apply adaptive exponential damping with treaty influence."""
    pi_star = 3.17300858012
    damp_base = exp(-pi_star * np.arange(len(signal)) / len(signal))
    if treaty_freq is not None:
        damp_mod = 1 + 0.1 * np.sin(2 * pi * treaty_freq * np.arange(len(signal)))
        return signal * damp_base * damp_mod
    return signal * damp_base

def dynamic_weights(time_phase):
    """Dynamic T/I/F weighting based on sky-law cycles."""
    return {
        "T": 0.4 * (1 + np.sin(2 * pi * time_phase)),
        "I": 0.3 * (1 - np.cos(2 * pi * time_phase)),
        "F": 0.3 * (1 + np.tan(pi * time_phase / 2) / 10)
    }

def phase_lock_recursive(phase_history, alpha=0.7):
    """Recursive phase locking with adaptive damping."""
    locked = 0.0
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history)
    return locked % (2 * pi), min(0.7, max(0.3, 0.5 + std_dev))

def treaty_harmonic_nodes(treaty_data):
    """Extract harmonic nodes from treaty spectrogram."""
    freq_domain = np.fft.fft(treaty_data)
    peaks = np.argsort(np.abs(freq_domain))[::-1][:3]
    return [freq_domain[p] / len(treaty_data) for p in peaks]

def damp_factor_from_std(std_dev):
    """Derive damp_factor from phase standard deviation."""
    return min(0.7, max(0.3, 0.5 + std_dev))