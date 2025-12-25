import numpy as np
import math
from scipy import signal
from collections import deque
# from brainflow... imports for real hooks (commented for sim)

BASE_EPSILON = 0.0417

LAYERS = {
    'macro': (0.1, 0.5),
    'meso': (0.5, 2.0),
    'microvascular': (2.0, 5.0),
    'cellular': (5.0, 10.0)
}

class HiPCTIntegrator:
    def __init__(self, fs=10, n_layers=len(LAYERS)):
        self.fs = fs
        self.n_layers = n_layers
        self.raw_buffer = deque(maxlen=int(10 * fs))  # Multi-layer vectors

    def simulate_vessel_signals(self):
        """Simulate multi-layer vessel flow (one vector per step)."""
        t = np.linspace(0, 1/self.fs, 1)
        signals = []
        for layer, (low, high) in LAYERS.items():
            freq = np.random.uniform(low, high)
            sig = np.sin(2 * np.pi * freq * t) + np.random.normal(0, 0.15)
            signals.append(sig[0])
        vector = np.array(signals)
        self.raw_buffer.append(vector)
        return vector

    # Real hook stub (uncomment for OpenBCI)
    # def get_real_eeg(self):
    #     # BrainFlow stream → vector of channel means or selected
    #     pass

class MeshNode:
    def __init__(self, name, baseline=0.6, fs=10):
        self.name = name
        self.baseline = baseline
        self.fs = fs
        self.current_epsilon = BASE_EPSILON
        self.raw_buffer = deque(maxlen=int(10 * fs))
        self.layer_powers = {layer: 0.0 for layer in LAYERS}

    def add_sample(self, vector):
        self.raw_buffer.append(vector)

    def compute_layer_powers(self):
        if len(self.raw_buffer) < self.fs * 2:
            return {layer: 0.0 for layer in LAYERS}  # Safe default
        
        data = np.stack(self.raw_buffer, axis=1)  # (layers, samples)
        layer_powers = {}
        total = 0.0
        
        for i, layer in enumerate(LAYERS):
            ch_data = data[i]
            f, psd = signal.welch(ch_data, fs=self.fs, nperseg=len(ch_data))
            power = np.trapz(psd, f)
            layer_powers[layer] = power
            total += power
        
        if total > 0:
            for layer in layer_powers:
                layer_powers[layer] /= total
        
        self.layer_powers = layer_powers
        return layer_powers

    def calculate_vitality(self):
        powers = self.compute_layer_powers()
        vitality = (
            powers['cellular'] * 0.3 +
            powers['microvascular'] * 0.4 -
            powers['macro'] * 0.2 -
            powers['meso'] * 0.1
        )
        vitality = max(0.5, min(1.5, vitality + 0.5))
        self.current_epsilon = BASE_EPSILON * vitality
        
        print(f"> {self.name} | Macro={powers['macro']:.2f} Cellular={powers['cellular']:.2f} "
              f"→ Vitality={vitality:.2f} ε_d={self.current_epsilon:.4f}")
        return vitality

# Demo (multi-layer sim)
def demo():
    print("=== FPT HiP-CT MULTI-LAYER VITALITY ===")
    integrator = HiPCTIntegrator()
    node = MeshNode("Brain_Node")
    
    for _ in range(120):  # Fill buffer
        integrator.simulate_vessel_signals()
        node.add_sample(integrator.raw_buffer[-1])
    
    for cycle in range(5):
        print(f"\nCycle {cycle+1}")
        integrator.simulate_vessel_signals()
        node.add_sample(integrator.raw_buffer[-1])
        node.calculate_vitality()

demo()