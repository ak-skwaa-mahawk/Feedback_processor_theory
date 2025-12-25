import numpy as np
import math
from scipy import signal
from collections import deque
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

BASE_EPSILON = 0.0417

# HiP-CT Layers as Vitality "Bands" (simulated or real freq ranges)
LAYERS = {
    'macro': (0.1, 0.5),     # Whole organ ~ slow waves
    'meso': (0.5, 2.0),      # Regional ~ alpha
    'microvascular': (2.0, 5.0),  # Capillaries ~ beta
    'cellular': (5.0, 10.0)  # Cellular ~ gamma
}

class HiPCTIntegrator:
    def __init__(self, fs=10):  # Simulated "sampling rate" for vessel flow
        self.fs = fs
        self.raw_buffer = deque(maxlen=int(10 * self.fs))  # 10-second buffer

    def simulate_vessel_signals(self, layer: str):
        """Simulate "vessel flow" as sinusoidal with noise (coherence proxy)."""
        low, high = LAYERS[layer]
        t = np.linspace(0, 10, int(10 * self.fs))
        signal = np.sin(2 * np.pi * np.random.uniform(low, high) * t) + np.random.normal(0, 0.2, len(t))
        self.raw_buffer.extend(signal)
        return signal

class MeshNode:
    def __init__(self, name, baseline_coherence=0.6, fs=10):
        self.name = name
        self.baseline = baseline_coherence
        self.fs = fs
        self.current_epsilon = BASE_EPSILON
        self.raw_buffer = deque(maxlen=int(10 * fs))  # 10-second buffer
        self.layer_powers = {layer: 0.0 for layer in LAYERS}

    def add_hipct_sample(self, sample):
        """Add simulated HiP-CT sample (vessel flow)."""
        self.raw_buffer.append(sample)

    def compute_layer_powers(self):
        """Extract "power" in each layer using Welch PSD."""
        if len(self.raw_buffer) < self.fs * 2:
            return  # Need sufficient data
        
        data = np.array(self.raw_buffer)
        
        # Welch PSD for smoother estimate
        f, psd = signal.welch(data, fs=self.fs, nperseg=len(data))
        
        total_power = np.trapz(psd, f)
        layer_powers = {}
        
        for layer, (low, high) in LAYERS.items():
            idx = np.where((f >= low) & (f <= high))[0]
            if len(idx) > 0:
                layer_powers[layer] = np.trapz(psd[idx], f[idx]) / total_power if total_power > 0 else 0
            else:
                layer_powers[layer] = 0.0
        
        self.layer_powers = layer_powers
        return layer_powers

    def calculate_vitality_from_hipct(self):
        """Psyselsic Vitality from HiP-CT layers."""
        powers = self.compute_layer_powers()
        
        # Coiled readiness: High "coherence" in micro/cellular (gamma), low disorder in macro (theta)
        vitality = (powers['cellular'] * 0.3 + powers['microvascular'] * 0.4) - (powers['macro'] * 0.2 + powers['meso'] * 0.1)
        vitality = (vitality + 0.5)  # Normalize ~0.5–1.5
        vitality = max(0.5, min(1.5, vitality))
        
        self.current_epsilon = BASE_EPSILON * vitality
        print(f"   > {self.name} HiP-CT: Macro={powers['macro']:.2f} Cellular={powers['cellular']:.2f} "
              f"→ Vitality={vitality:.2f} → ε_d={self.current_epsilon:.4f}")
        return vitality

    # ... (observe, vhitzee_correct unchanged)

# --- HiP-CT Vitality Mesh Demo ---
def run_hipct_vitality_demo():
    print("=== FPT HiP-CT VITALITY MESH DEMO ===")
    integrator = HiPCTIntegrator()
    node = MeshNode("HiPCT_Node")
    
    for cycle in range(3):
        print(f"\nCycle {cycle+1}:")
        for layer in LAYERS:
            signal = integrator.simulate_vessel_signals(layer)  # Vessel flow as "EEG"
            node.add_hipct_sample(np.mean(signal))  # Average as scalar for sim
        node.calculate_vitality_from_hipct()

run_hipct_vitality_demo()</parameter>
</xai:function_call>
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