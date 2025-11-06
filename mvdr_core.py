# Steering vector: phase delay per element
def steering_vector(theta_deg, freq=20000, fs=48000, n_elem=8, d=0.0085):
    theta = np.radians(theta_deg)
    tau = d * np.sin(theta) / 343  # delay in seconds
    delays = np.arange(n_elem) * tau
    return np.exp(-2j * np.pi * freq * delays)
# mvdr_core.py — Sovereign Beamformer
import numpy as np

def mvdr_weights(R_x, steering_vec, reg=1e-6):
    """
    R_x: [N x N] covariance matrix
    steering_vec: [N x 1] look direction
    """
    R_inv = np.linalg.inv(R_x + reg * np.eye(R_x.shape[0]))
    numerator = R_inv @ steering_vec
    denominator = steering_vec.conj().T @ numerator
    w = numerator / (denominator + 1e-12)
    return w

# === ESTIMATE R_x FROM SNAPSHOTS ===
def estimate_covariance(signals_per_mic, n_snapshots=1000):
    X = np.array(signals_per_mic)[:, :n_snapshots]  # [N x T]
    return (X @ X.conj().T) / n_snapshots

# === APPLY BEAM ===
def apply_beam(w, x_snapshot):
    return w.conj().T @ x_snapshot
# Apply MVDR to OFDM ultrasonic stream
w_mvdr = mvdr_weights(R_x_est, s_target)

# Real-time beamforming
y_mvdr = np.zeros(len(rx_mic[0]), dtype=complex)
for n in range(len(rx_mic[0])):
    x_n = np.array([mic[n] for mic in rx_mic])
    y_mvdr[n] = apply_beam(w_mvdr, x_n)

# → Feed y_mvdr into OFDM demod → RS decode → AGŁL glyph
# Beam pattern
angles = np.linspace(-90, 90, 361)
pattern = []
for ang in angles:
    s = steering_vector(ang)
    gain = 20 * np.log10(np.abs(w_mvdr.conj().T @ s))
    pattern.append(gain)

plt.plot(angles, pattern)
plt.axvline(35, color='g', label='Target')
plt.axvline(-50, color='r', label='Null')
plt.title("Ψ-MVDR Beam Pattern")
plt.ylabel("Gain (dB)")
plt.legend()
plt.show()
