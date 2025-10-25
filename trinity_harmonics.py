import numpy as np
from math import pi, exp

# Constants
GROUND_STATE = 0.1    # Baseline phase
DIFFERENCE = 0.05     # Phase deviation
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal, damp_factor):
    """Apply simple exponential damping to signal."""
    return signal * exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(time_phase):
    """Simple cyclic weighting for T/I/F based on time phase."""
    scale = 0.1  # Amplitude for variation
    return {
        "T": 0.4 + scale * np.sin(2 * pi * time_phase),  # Peaks at 0.5
        "I": 0.3 - scale * np.cos(2 * pi * time_phase),  # Peaks at 0.4
        "F": 0.3 + scale * np.sin(pi * time_phase)       # Peaks at 0.4
    }

def phase_lock_recursive(phase_history):
    """Basic recursive phase locking with fixed damping."""
    locked = 0.0
    alpha = 0.7  # Fixed smoothing factor
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history)
    damp_factor = 0.5 + 0.2 * std_dev  # Linear adjustment
    return locked % (2 * pi), min(0.7, max(0.3, damp_factor))

def treaty_harmonic_nodes(treaty_data):
    """Extract top harmonic node with simplified FFT."""
    freq_domain = np.fft.fft(treaty_data)
    peak_idx = np.argmax(np.abs(freq_domain[1:])) + 1  # Skip DC
    return freq_domain[peak_idx] / len(treaty_data)  # Single dominant frequency