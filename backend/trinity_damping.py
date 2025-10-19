import numpy as np

def trinity_damping(values, factor=0.5):
    phase = 2 * np.pi * np.linspace(0, 1, len(values))
    oscillation = np.sin(phase) * 0.197
    damped = values * (1 - factor * oscillation)
    return np.clip(damped, 0, 1)