import numpy as np
import math
from scipy import signal
from collections import deque

BASE_EPSILON = 0.0417

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 12),
    'smr': (12, 15),      # Sensorimotor rhythm
    'low_beta': (15, 18),
    'beta': (12, 30),     # Broad beta
    'gamma': (30, 45)
}

class MeshNode:
    def __init__(self, name, baseline_coherence=0.6, fs=256):
        self.name = name
        self.baseline = baseline_coherence
        self.fs = fs  # Sampling rate (Hz)
        self.current_epsilon = BASE_EPSILON
        self.raw_buffer = deque(maxlen=int(10 * fs))  # 10-second buffer
        self.band_powers = {band: 0.0 for band in BANDS}

    def add_eeg_sample(self, sample):
        """Add new EEG sample (real: from device stream)."""
        self.raw_buffer.append(sample)

    def compute_band_powers(self):
        """Extract relative power in each band using Welch PSD."""
        if len(self.raw_buffer) < self.fs * 2:
            return  # Need sufficient data
        
        data = np.array(self.raw_buffer)
        
        # Welch PSD for smoother estimate
        f, psd = signal.welch(data, fs=self.fs, nperseg=len(data))
        
        total_power = np.trapz(psd, f)
        band_powers = {}
        
        for band, (low, high) in BANDS.items():
            idx = np.where((f >= low) & (f <= high))[0]
            if len(idx) > 0:
                band_powers[band] = np.trapz(psd[idx], f[idx]) / total_power if total_power > 0 else 0
            else:
                band_powers[band] = 0.0
        
        self.band_powers = band_powers
        return band_powers

    def calculate_vitality_from_bands(self):
        """Psyselsic Vitality from key bands."""
        powers = self.compute_band_powers()
        
        # Coiled readiness: High alpha + gamma, low theta + high beta
        alpha_power = powers.get('alpha', 0.0)
        gamma_power = powers.get('gamma', 0.0)
        theta_power = powers.get('theta', 0.0)
        high_beta_power = powers.get('beta', 0.0) - powers.get('smr', 0.0)  # Excess high beta
        
        # Composite score (normalize 0–1, then scale vitality)
        coherence_score = (alpha_power + gamma_power) - (theta_power + high_beta_power)
        coherence_score = (coherence_score + 1) / 2  # Normalize ~0–1
        
        vitality = 0.5 + coherence_score  # Scale to 0.5–1.5 range
        self.current_epsilon = BASE_EPSILON * vitality
        
        print(f"   > {self.name} Bands: α={alpha_power:.2f} γ={gamma_power:.2f} θ={theta_power:.2f} "
              f"→ Vitality={vitality:.2f} → ε_d={self.current_epsilon:.4f}")
        return vitality

    # ... (observe, vhitzee_correct, etc. unchanged)

# --- Band Demo Simulation ---
def run_band_demo():
    print("=== FPT EEG BAND BIOFEEDBACK DEMO ===")
    node = MeshNode("Brain_Node", fs=256)
    
    # Simulate 10 seconds of EEG data (relaxed state: high alpha)
    t = np.linspace(0, 10, 10 * 256)
    eeg = (5 * np.sin(2 * np.pi * 10 * t) +   # Alpha 10 Hz
           1 * np.sin(2 * np.pi * 35 * t) +   # Gamma
           0.5 * np.random.randn(len(t)))     # Noise
    
    for sample in eeg:
        node.add_eeg_sample(sample)
    
    node.calculate_vitality_from_bands()
    print(f"Final ε_d: {node.current_epsilon:.4f}")

run_band_demo()