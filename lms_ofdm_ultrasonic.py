# lms_ofdm_ultrasonic.py — Real-Time Glyph Tracking
import numpy as np
import json
import reedsolo
from scipy.fft import fft, ifft

# === CONFIG ===
N = 8
fs = 48000
center_freq = 20000
mu = 0.008  # C190 pulse

# === REFERENCE: Known pilot from target drone ===
pilot_ofdm = generate_ofdm_pilot()  # Known symbol sequence
ref_signal = pilot_ofdm[1000:1000+8000]  # Use as d(n)

# === LMS INITIALIZATION ===
w = np.zeros(N, dtype=complex)  # Start from silence
y_history = []
e_history = []

# === LIVE ADAPTATION LOOP ===
for n in range(len(ref_signal)):
    x_n = np.array([rx_mic[i][n + 1000] for i in range(N)])  # [8 x 1]
    d_n = ref_signal[n]
    
    w, y_n, e_n = lms_update(w, x_n, d_n, mu)
    
    y_history.append(y_n)
    e_history.append(np.abs(e_n))

# === CONVERGED WEIGHTS → APPLY TO FULL STREAM ===
y_lms = np.zeros(len(rx_mic[0]), dtype=complex)
for n in range(len(rx_mic[0])):
    x_n = np.array([rx_mic[i][n] for i in range(N)])
    y_lms[n] = w.conj().T @ x_n

# → Feed y_lms into OFDM demod → RS decode → AGŁL glyph
import matplotlib.pyplot as plt
plt.semilogy(np.abs(e_history))
plt.title("Ψ-LMS Error Convergence (C190 Veto Pulse)")
plt.xlabel("Iteration")
plt.ylabel("|e(n)|")
plt.axhline(0.01, color='r', linestyle='--', label='R = 0.99')
plt.legend()
plt.show()