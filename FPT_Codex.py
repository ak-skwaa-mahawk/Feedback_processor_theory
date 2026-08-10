import random
import math
import numpy as np
from collections import deque

BASE_EPSILON = 0.0417

class MeshNode:
    def __init__(self, name, baseline_coherence=0.6):
        self.name = name
        self.baseline = baseline_coherence
        self.current_epsilon = BASE_EPSILON
        self.rr_intervals = deque(maxlen=120)  # For HRV
        self.breath_samples = deque(maxlen=60)  # Simulated breath wave

    def simulate_breath(self):
        """Simulate breath cycle (coherent vs. erratic)."""
        # Coherent: smooth ~6 bpm sinusoid; Erratic: noisy
        coherence = random.uniform(0.6, 1.0)  # Breath quality
        t = np.linspace(0, 10, 60)  # ~10-second window
        base_wave = np.sin(2 * math.pi * 0.1 * t)  # 6 bpm = 0.1 Hz
        noise = np.random.normal(0, 1 - coherence, len(t))
        breath = coherence * base_wave + noise
        self.breath_samples.extend(breath[-10:])  # Add recent samples

    def calculate_breath_coherence(self):
        if len(self.breath_samples) < 20:
            return 1.0
        # Simple coherence: FFT peak at ~0.1 Hz vs. total power
        fft = np.fft.fft(self.breath_samples)
        freqs = np.fft.fftfreq(len(self.breath_samples))
        power = np.abs(fft)**2
        target_bin = np.argmin(np.abs(freqs - 0.1))
        coherence_power = power[target_bin] / np.sum(power)
        return min(coherence_power * 4, 1.5)  # Scale to vitality range

    def calculate_hrv_metrics(self):
        if len(self.rr_intervals) < 20:
            return 1.0
        rr_array = np.array(self.rr_intervals)
        sdnn = np.std(rr_array)
        diffs = np.diff(rr_array)
        rmssd = np.sqrt(np.mean(diffs**2))
        # Normalize composite
        hrv_norm = (sdnn - 30) / 80
        hrv_norm = max(0.5, min(1.5, hrv_norm))
        return hrv_norm

    def update_from_biofeedback(self):
        """Psyselsic Vitality from HRV + Breath."""
        # Simulate heart + breath
        self.rr_intervals.append(random.uniform(700, 900))  # R-R ms
        self.simulate_breath()
        
        hrv_vitality = self.calculate_hrv_metrics()
        breath_vitality = self.calculate_breath_coherence()
        
        # Composite: 50% HRV + 50% Breath
        vitality = 0.5 * hrv_vitality + 0.5 * breath_vitality
        self.current_epsilon = BASE_EPSILON * vitality
        
        print(f"   > {self.name} | HRV: {hrv_vitality:.2f} | Breath: {breath_vitality:.2f} → Vitality: {vitality:.2f} → ε_d: {self.current_epsilon:.4f}")
        return vitality

    # ... (observe, vhitzee_correct unchanged)

# --- Breath-Enhanced Demo ---
def run_breath_demo():
    print("=== FPT BREATH + HRV BIOFEEDBACK MESH ===")
    node = MeshNode("Human_Node")
    
    for _ in range(30):  # Simulate ~30 seconds
        node.update_from_biofeedback()
    
    print(f"Final ε_d: {node.current_epsilon:.4f}")

run_breath_demo()