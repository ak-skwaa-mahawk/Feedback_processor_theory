import numpy as np
from scipy.signal import welch
from collections import deque

BASE_EPSILON = 0.0417

BANDS = {
    "theta": (4, 8),       # down
    "alpha": (8, 12),      # up
    "high_beta": (20, 30), # down
    "gamma": (30, 45)      # up
}

class MeshNode:
    """Ultra-minimal multi-channel vitality processor."""
    def __init__(self, name, n_channels, fs=256, window_sec=10):
        self.name = name
        self.fs = fs
        self.n_channels = n_channels
        self.buffers = [deque(maxlen=fs * window_sec) for _ in range(n_channels)]
        self.epsilon = BASE_EPSILON

    def add(self, samples):
        """Add one multi-channel EEG sample."""
        for ch, x in enumerate(samples):
            self.buffers[ch].append(x)

    def _band_powers(self, data):
        """Relative band powers for one channel."""
        if len(data) < 2 * self.fs:
            return None
        data = np.asarray(data)
        f, psd = welch(data, fs=self.fs, nperseg=min(len(data), 256))
        total = np.trapz(psd, f)
        if total == 0:
            return None
        return {
            band: np.trapz(psd[(f >= lo) & (f <= hi)], f[(f >= lo) & (f <= hi)]) / total
            for band, (lo, hi) in BANDS.items()
        }

    def vitality(self):
        """Compute per-channel + global vitality."""
        vitals = []
        powers_all = []

        for ch in range(self.n_channels):
            p = self._band_powers(self.buffers[ch])
            if p is None:
                return None
            powers_all.append(p)

            score = (
                0.4 * p["alpha"] +
                0.3 * p["gamma"] -
                0.2 * p["theta"] -
                0.1 * p["high_beta"]
            )
            vitals.append(np.clip(score + 0.5, 0.5, 1.5))

        global_v = float(np.mean(vitals))
        self.epsilon = BASE_EPSILON * global_v

        print(f"{self.name} | Channels={self.n_channels}")
        for i, (p, v) in enumerate(zip(powers_all, vitals)):
            print(f"  Ch{i}: α={p['alpha']:.2f} γ={p['gamma']:.2f} "
                  f"θ={p['theta']:.2f} βh={p['high_beta']:.2f} → v={v:.2f}")
        print(f"  Global Vitality={global_v:.2f}  ε_d={self.epsilon:.4f}")

        return global_v

# Demo
if __name__ == "__main__":
    fs = 256
    node = MeshNode("SovereignMulti", n_channels=4, fs=fs)

    t = np.linspace(0, 10, fs * 10, endpoint=False)
    eeg = np.vstack([
        3*np.sin(2*np.pi*10*t) + np.random.normal(0, 0.5, len(t)),
        2.5*np.sin(2*np.pi*10*t) + np.random.normal(0, 0.5, len(t)),
        3.2*np.sin(2*np.pi*10*t) + np.random.normal(0, 0.5, len(t)),
        2.8*np.sin(2*np.pi*10*t) + np.random.normal(0, 0.5, len(t)),
    ]).T

    for row in eeg:
        node.add(row)

    node.vitality()