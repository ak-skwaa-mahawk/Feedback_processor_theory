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
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
import time

class OpenBCIIntegrator:
    def __init__(self, board_type=BoardIds.CYTON_BOARD, serial_port=None):
        params = BrainFlowInputParams()
        params.serial_port = serial_port  # e.g., 'COM3' Windows, '/dev/ttyUSB0' Linux
        self.board_id = board_type
        self.board = BoardShim(self.board_id, params)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)

    def start_session(self):
        self.board.prepare_session()
        self.board.start_stream()

    def get_latest_samples(self, num_samples=256):
        data = self.board.get_board_data(num_samples)
        eeg_data = data[self.eeg_channels]  # Shape: (channels, samples)
        return eeg_data

    def stop_session(self):
        self.board.stop_stream()
        self.board.release_session()

# --- Tie into FPT MeshNode (Example Extension) ---
# In MeshNode.update_from_biofeedback():
def integrate_openbci(self, integrator, channel=0):
    """Use real OpenBCI data instead of simulation."""
    eeg_data = integrator.get_latest_samples()
    if eeg_data.size > 0:
        channel_data = eeg_data[channel]  # Single channel for simplicity
        # Feed to band power/HRV calc (replace simulate)
        self.raw_buffer.extend(channel_data[-self.fs*2:])  # Fill buffer

# --- Demo Usage ---
if __name__ == "__main__":
    # Example for Cyton USB
    integrator = OpenBCIIntegrator(board_type=BoardIds.CYTON_BOARD, serial_port='COM3')  # Adjust port
    integrator.start_session()
    
    node = MeshNode("OpenBCI_Node")
    try:
        for _ in range(50):
            node.integrate_openbci(integrator)
            node.calculate_vitality_from_bands()
            time.sleep(0.1)
    finally:
        integrator.stop_session()