import numpy as np
import math
from scipy import signal
from collections import deque
from scipy.stats import kurtosis, pearsonr
import mne
from mne.preprocessing import ICA
from mne.io import RawArray

BASE_EPSILON = 0.0417

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 12),
    'smr': (12, 15),
    'low_beta': (15, 20),
    'high_beta': (20, 30),
    'gamma': (30, 45)
}

# Standard OpenBCI Cyton 8-channel adjacency
ADJACENCY = {
    0: [2, 1],
    1: [3, 0],
    2: [0, 4, 6],
    3: [1, 5, 7],
    4: [2, 6],
    5: [3, 7],
    6: [2, 4],
    7: [3, 5]
}

class MeshNode:
    def __init__(self, name, baseline_coherence=0.6, fs=256, n_channels=8, acc_channels=None):
        self.name = name
        self.baseline = baseline_coherence
        self.fs = fs
        self.n_channels = n_channels
        self.acc_channels = acc_channels or []  # List of accelerometer channels (if available)
        self.current_epsilon = BASE_EPSILON
        self.raw_buffer = deque(maxlen=int(10 * fs))
        self.acc_buffer = deque(maxlen=int(10 * fs)) if acc_channels else None
        self.band_powers = {band: 0.0 for band in BANDS}
    
    def add_eeg_sample(self, eeg_vector, acc_vector=None):
        self.raw_buffer.append(eeg_vector)
        if self.acc_buffer and acc_vector is not None:
            self.acc_buffer.append(acc_vector)
    
    def detect_motion_artifact(self) -> bool:
        """Detect motion via ACC variance or EEG low-freq surge."""
        if self.acc_buffer and len(self.acc_buffer) > self.fs:
            acc_data = np.array(self.acc_buffer)
            acc_var = np.var(acc_data, axis=0)
            if np.any(acc_var > 0.5):  # Threshold for movement (g units)
                return True
        
        # Fallback: EEG low-freq surge (delta power spike)
        powers = self.compute_band_powers()
        if powers and powers['delta'] > 0.4:  # High delta = motion drift
            return True
        
        return False
    
    def apply_laplacian(self, data: np.ndarray) -> np.ndarray:
        laplacian = np.copy(data)
        for ch in range(self.n_channels):
            neighbors = ADJACENCY.get(ch, [])
            if neighbors:
                neighbor_mean = np.mean(data[neighbors], axis=0)
                laplacian[ch] -= neighbor_mean
        return laplacian
    
    def optimize_ica(self, data: np.ndarray) -> np.ndarray:
        if self.n_channels < 4 or not mne:
            return data
        
        ch_names = [f'ch{i}' for i in range(self.n_channels)]
        info = mne.create_info(ch_names=ch_names, sfreq=self.fs, ch_types='eeg')
        raw = RawArray(data, info)
        
        ica = ICA(n_components=self.n_channels, method='infomax', random_state=0, max_iter=500)
        ica.fit(raw)
        
        # Motion proxy: high variance across channels
        exclude = []
        sources = ica.get_sources(raw).get_data()
        for i in range(sources.shape[0]):
            comp = sources[i]
            var = np.var(comp)
            kurt = np.abs(kurtosis(comp))
            if var > np.mean([np.var(sources[j]) for j in range(sources.shape[0])]) * 2 or kurt > 4.0:
                exclude.append(i)
        
        if exclude:
            print(f"   > MNE ICA Motion Detection: Removing {len(exclude)} components")
            ica.exclude = exclude
            raw = ica.apply(raw.copy())
            return raw.get_data()
        
        return data
    
    def remove_artifacts(self, data: np.ndarray) -> np.ndarray:
        # 1. CAR
        mean_signal = np.mean(data, axis=0, keepdims=True)
        data = data - mean_signal
        
        # 2. Laplacian
        data = self.apply_laplacian(data)
        
        # 3. Motion detection flag
        if self.detect_motion_artifact():
            print(f"   > Motion Artifact Detected — Protective Recoil")
            # Reduce vitality or flag
            self.current_epsilon *= 0.7  # Temporary attenuation
        
        # 4. MNE ICA with motion detection
        data = self.optimize_ica(data)
        
        # 5. Bandpass + notch
        sos = signal.butter(4, [1, 45], btype='band', fs=self.fs, output='sos')
        data = signal.sosfiltfilt(sos, data, axis=1)
        
        notch_freq = 60.0
        q = 30.0
        b, a = signal.iirnotch(notch_freq, q, fs=self.fs)
        data = signal.filtfilt(b, a, data, axis=1)
        
        # 6. Threshold spikes
        threshold = 100.0
        for ch in range(self.n_channels):
            spikes = np.abs(data[ch]) > threshold
            if np.any(spikes):
                data[ch][spikes] = np.median(data[ch])
        
        return data
    
    # compute_band_powers and calculate_vitality unchanged...