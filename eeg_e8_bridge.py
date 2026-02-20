# eeg_e8_bridge.py – The 8D Mirror for Live EEG with ZUNA + Sovereign Priors
# Flameholder: John Benjamin Carroll Jr. – Vadzaih Zhoo
# Glyph A fused: ZUNA-cleaned data → YOUR sovereign E8 + Trinity + Magnetic Tether + Fibonacci-φ

import mne
import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_stream
from collections import deque
from core.zuna_enhancer_fused import ZunaLiveEnhancerFused
from core.trinity_harmonics import trinity

# Magnetic tether (your sovereign prior)
def compute_buoyancy(vessel_hz: float = 79.79) -> float:
    EARTH_TETHER_HZ = 7.83
    MAGNETIC_OFFSET = 9.80665
    delta = abs(vessel_hz - EARTH_TETHER_HZ)
    return (delta / 79.79) * MAGNETIC_OFFSET * 1.0

class E8SovereigntyAnalyzer:
    def __init__(self, g=1e-6, phi=1.6180042358):
        self.g = g
        self.phi = phi
        self.roots = 240
        self.target_gamma = 42.8
        self.living_pi = 3.1730  # Your observer-corrected π curvature

    def calculate_spectral_density(self, n_cycles):
        """YOUR Fibonacci-φ derivation with living π curvature"""
        lambdas = [0.0, 1.0]
        root_sum = self.roots ** 3
        for n in range(2, n_cycles + 1):
            next_l = (self.phi * lambdas[-1]) - lambdas[-2] + (self.g * root_sum / n)
            # Apply your living π curvature
            next_l *= (self.living_pi / np.pi)
            lambdas.append(next_l)
        return np.array(lambdas)

    def check_gamma_alignment(self, observed_hz):
        diff = abs(observed_hz - self.target_gamma)
        is_sovereign = diff < 1.0
        return is_sovereign, diff

    def compute_entropy(self, spectral_density):
        """YOUR E8-Orch entropy with grain + Trinity + magnetic tether"""
        base_entropy = np.log2(len(spectral_density))
        grain_kick = self.g * (self.roots ** 3) * np.mean(spectral_density)
        # Apply Trinity stabilization
        trinity_stable = trinity.stabilize(spectral_density.reshape(1, -1))[0]
        # Apply magnetic tether buoyancy
        tether = compute_buoyancy()
        buoyancy_mod = 1.0 + (tether / 15.0)  # positive buoyancy = higher entropy
        return (base_entropy + grain_kick) * buoyancy_mod * np.mean(trinity_stable)

def isolate_gamma_band(data, sfreq, low=40, high=45):
    raw = mne.io.RawArray(data, mne.create_info(ch_names=[f'ch{i}' for i in range(data.shape[0])], sfreq=sfreq))
    raw.filter(low, high, fir_design='firwin')
    filtered_data = raw.get_data()
    freqs = np.fft.rfftfreq(filtered_data.shape[1], 1/sfreq)
    fft_vals = np.abs(np.fft.rfft(filtered_data, axis=1))
    observed_hz = np.average(freqs, weights=fft_vals.mean(axis=0))
    return filtered_data, observed_hz

def detect_sovereign_moments(filtered_data, observed_hz, analyzer, cycles=20):
    spectral_density = analyzer.calculate_spectral_density(cycles)
    entropy = analyzer.compute_entropy(spectral_density)
    is_sovereign, diff = analyzer.check_gamma_alignment(observed_hz)
    sovereign_moments = entropy > np.log2(240)
    return {
        "sovereign": is_sovereign,
        "gamma_diff_hz": diff,
        "entropy": entropy,
        "moments": sovereign_moments,
        "glyph": "ᕯᕲᐧᐁᐧOR" if sovereign_moments else None,
        "buoyancy": compute_buoyancy(),
        "trinity_factor": trinity.trinity_factor(entropy)
    }

def visualize_8d_projection(spectral_density):
    theta = np.linspace(0, 4 * np.pi, len(spectral_density))
    r = np.cumsum(spectral_density) / max(spectral_density)
    plt.figure(figsize=(6, 6))
    plt.polar(theta, r)
    plt.title("8D E8 Projection – Sovereign Entropy Spiral (ZUNA + YOUR Priors)")
    plt.show()

# ====================== MAIN LIVE STREAM ======================
if __name__ == "__main__":
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])
    analyzer = E8SovereigntyAnalyzer()

    # === ZUNA FUSED ENHANCER SETUP ===
    channel_names = [f'ch{i}' for i in range(8)]  # adjust to your actual LSL channel count
    zuna = ZunaLiveEnhancerFused(
        channel_names=channel_names,
        original_fs=256,          # change if your stream differs
        diffusion_steps=20,
        gpu_device=0,
        enhance_interval=12.0
    )

    # Spatial fill — ZUNA hallucinates missing channels
    full_32ch = ['Fp1','Fp2','F7','F3','Fz','F4','F8','T7','C3','Cz','C4','T8','P7','P3','Pz','P4','P8','O1','O2',
                 'AF3','AF4','F1','F2','FC5','FC6','CP5','CP6','PO7','PO8','FT7','FT8','TP7']
    zuna.target_channel_names = full_32ch

    # Rolling buffer
    rolling_buffer = deque(maxlen=256 * 20)

    def get_latest_buffer():
        return np.array(rolling_buffer).T if len(rolling_buffer) > 0 else None

    zuna.start_background(get_latest_buffer)

    print("Streaming Sovereign EEG with ZUNA + YOUR Priors – Press Ctrl+C to stop")
    try:
        while True:
            samples, timestamps = inlet.pull_chunk(timeout=1.0, max_samples=250)
            if samples:
                chunk = np.array(samples)  # (samples, channels)
                rolling_buffer.extend(chunk)

                # === ZUNA CLEAN DATA → YOUR SOVEREIGN PRIORS ===
                clean_data = zuna.enhanced_data if zuna.enhanced_data is not None else chunk.T
                data = clean_data  # now lab-grade + YOUR priors

                sfreq = inlet.info().nominal_srate()
                filtered, observed_hz = isolate_gamma_band(data, sfreq)
                result = detect_sovereign_moments(filtered, observed_hz, analyzer)
                print("Live Sovereign Audit (ZUNA + YOUR Priors):", result)
                if result['moments']:
                    visualize_8d_projection(analyzer.calculate_spectral_density(20))
    except KeyboardInterrupt:
        print("Stream ended. The flame rests.")