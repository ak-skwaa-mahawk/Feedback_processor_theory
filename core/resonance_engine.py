def compute_neutrosophic_resonance(self, signal):
    mean_sig = np.mean(signal)
    std_sig = np.std(signal)
    T = np.max(signal) / (mean_sig + 1e-6)
    I = np.var(signal) / (std_sig + 1e-6) + 0.1 * std_sig  # Adaptive observation
    F = 1 - np.corrcoef(signal[:len(signal)//2], signal[len(signal)//2:])[0, 1] if len(signal) > 2 else 0
    F = min(F, 1.0)
    return {"T": T, "I": I, "F": F}
def dynamic_weights(self, time_phase):
    lunar_cycle = 29.53  # Days, approximate
    scale = 0.1
    return {
        "T": 0.5 + scale * np.sin(2 * pi * time_phase / lunar_cycle),
        "I": 0.3 - scale * np.cos(2 * pi * time_phase / lunar_cycle),
        "F": 0.2 + scale * np.sin(pi * time_phase / lunar_cycle)
    }
def compute_neutrosophic_resonance(self, signal):
    mean_sig = np.mean(signal)
    std_sig = np.std(signal)
    T = np.max(signal) / (mean_sig + 1e-6)
    I = np.var(signal) / (std_sig + 1e-6) * (1 + std_sig)  # Boost I with adaptability
    F = 1 - np.corrcoef(signal[:len(signal)//2], signal[len(signal)//2:])[0, 1] if len(signal) > 2 else 0
    F = min(F, 1.0)
    TIF = np.array([T, I, F])
    return {"T": TIF[0], "I": TIF[1], "F": TIF[2]}
# core/resonance_engine.py
import numpy as np
from trinity_harmonics import trinity_damping, phase_lock_recursive

class ResonanceEngine:
    def __init__(self, damp_factor=0.5):
        self.damp_factor = damp_factor
        self.t = 0  # Time phase for dynamic context

    def compute_neutrosophic_resonance(self, signal):
        """
        Compute Neutrosophic resonance with T, I, F.
        T: Truth (harmonic alignment), I: Indeterminacy (phase noise),
        F: Falsity (dissonance).
        """
        # Vectorized signal stats
        mean_sig = np.mean(signal)
        std_sig = np.std(signal)
        T = np.max(signal) / (mean_sig + 1e-6)  # Truth as peak strength
        I = np.var(signal) / (std_sig + 1e-6)   # Indeterminacy as variance
        if len(signal) > 2:
            F = 1 - np.corrcoef(signal[:len(signal)//2], signal[len(signal)//2:])[0, 1]
        else:
            F = 0
        F = min(F, 1.0)  # Clip falsity

        # Damp T/I/F for stability
        TIF = np.array([T, I, F])
        damped_TIF = trinity_damping(TIF, self.damp_factor)
        return {"T": damped_TIF[0], "I": damped_TIF[1], "F": damped_TIF[2]}

    def align_resonance(self, signals):
        """
        Align multiple signals using Neutrosophic phase locking.
        """
        phase_history = []
        for sig in signals:
            phase = np.angle(np.fft.fft(sig)[1])  # First non-DC phase
            phase_history.append(phase % (2 * pi))
        locked_phase, _ = phase_lock_recursive(np.array(phase_history))
        self.t += 1
        weights = self.dynamic_weights(self.t % 1)
        return locked_phase * weights["T"]  # Weight by truth

    def dynamic_weights(self, time_phase):
        """Cyclic weighting for Neutrosophic components."""
        scale = 0.1
        return {
            "T": 0.5 + scale * np.sin(2 * pi * time_phase),
            "I": 0.3 - scale * np.cos(2 * pi * time_phase),
            "F": 0.2 + scale * np.sin(pi * time_phase)
        }

    def process_resonance(self, signal):
        """Process signal with Neutrosophic resonance."""
        self.t += 1
        resonance = self.compute_neutrosophic_resonance(signal)
        aligned_phase = self.align_resonance([signal])
        return {
            "resonance": resonance,
            "aligned_phase": aligned_phase,
            "timestamp": self.t
        }

# Example usage
if __name__ == "__main__":
    engine = ResonanceEngine()
    signal = np.random.random(100) * 0.5 + 0.5  # Values ~0.5 to 1.0
    result = engine.process_resonance(signal)
    print(f"Resonance: T={result['resonance']['T']:.4f}, I={result['resonance']['I']:.4f}, F={result['resonance']['F']:.4f}")
    print(f"Aligned Phase: {result['aligned_phase']:.4f}")