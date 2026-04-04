import numpy as np
from math import pi
from typing import Dict, Tuple, List, Optional

# ====================== TRINITY HARMONICS v0.4.3 (Canonical) ======================
GROUND_STATE = 0.1
DIFFERENCE = 0.05
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal: np.ndarray, damp_factor: float) -> np.ndarray:
    """Fixed exponential damping (vectorized)."""
    return signal * np.exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(time_phase: float) -> Dict[str, float]:
    """Cyclic T/I/F weighting (exactly as you wrote)."""
    scale = 0.1
    return {
        "T": 0.4 + scale * np.sin(2 * pi * time_phase),
        "I": 0.3 - scale * np.cos(2 * pi * time_phase),
        "F": 0.3 + scale * np.sin(pi * time_phase)
    }

def phase_lock_recursive(phase_history: List[float]) -> Tuple[float, float]:
    """Recursive EMA phase lock + adaptive damp_factor."""
    locked = 0.0
    alpha = 0.7
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history) if len(phase_history) > 1 else 0.0
    damp_factor = 0.5 + 0.2 * std_dev
    return locked % (2 * pi), min(0.7, max(0.3, damp_factor))

def treaty_harmonic_nodes(treaty_data: List[float]) -> complex:
    """FFT peak = dominant harmonic node (aligns with Kyoto W-state Fourier tech)."""
    freq_domain = np.fft.fft(treaty_data)
    peak_idx = np.argmax(np.abs(freq_domain[1:])) + 1
    return freq_domain[peak_idx] / len(treaty_data)

# ====================== WSTATE ENTANGLEMENT (now powered by v0.4.3) ======================
class WStateEntanglement:
    def __init__(self):
        self.w_state: Dict[str, float] = {'100': 1.0/3, '010': 1.0/3, '001': 1.0/3}
        self.fidelity: float = 1.0
        self.phase_history: List[float] = []

    def measure_fidelity(self, w_state: Dict[str, float]) -> float:
        ideal = 1.0 / 3
        deviation = sum(abs(v - ideal)**2 for v in w_state.values())
        return max(0.0, 1.0 - deviation)

    def update(self,
               obj: Optional[Dict[str, float]] = None,
               time_phase: float = 0.0,
               use_dynamic_weights: bool = True,
               damp_preset: str = "Balanced") -> Tuple[Dict[str, float], float]:
        """Full update: dynamic weights → damping → normalize → fidelity."""
        if use_dynamic_weights:
            weights = dynamic_weights(time_phase)
        else:
            weights = obj or {"T": 1.0, "I": 1.0, "F": 1.0}

        # Neutrosophic scaling
        w = np.array([self.w_state['100'] * weights["T"],
                      self.w_state['010'] * weights["I"],
                      self.w_state['001'] * weights["F"]])

        # Apply Trinity damping
        damp_factor = DAMPING_PRESETS.get(damp_preset, 0.5)
        w = trinity_damping(w, damp_factor)

        # Normalize
        total = np.sum(w)
        if total > 0:
            w = w / total
        else:
            w = np.array([1.0/3, 1.0/3, 1.0/3])

        self.w_state = {'100': w[0], '010': w[1], '001': w[2]}
        self.fidelity = self.measure_fidelity(self.w_state)
        self.phase_history.append(time_phase)
        return self.w_state, self.fidelity


# ====================== EXAMPLE RUN ======================
if __name__ == "__main__":
    we = WStateEntanglement()
    print("=== Dynamic W-state evolution over 4 phases ===")
    for phase in np.linspace(0, 2, 5):
        state, fid = we.update(time_phase=phase, damp_preset="Balanced")
        print(f"Phase {phase:.2f} → W-state: {state} | Fidelity: {fid:.4f}")
    
    print("\nDominant harmonic node (treaty-style FFT):")
    sample_data = [0.33, 0.34, 0.32, 0.35]  # simulated W amplitudes
    print(treaty_harmonic_nodes(sample_data))