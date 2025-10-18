from trinity_harmonics import GROUND_STATE, trinity_damping

class ResonanceEngine:
    def analyze_coherence(self, signal):
        damped_signal = trinity_damping(signal)
        coherence = np.mean(np.abs(damped_signal)) / GROUND_STATE  # Normalized score
        return {"coherence": coherence, "damped_signal": damped_signal.tolist()}