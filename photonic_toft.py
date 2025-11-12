# photonic_toft.py
# Photonic TOFT Modulator — Bistable 79Hz Resonance Sim
# Based on "Enhanced optical bistability..." Nature paper
# Author: Grok (inspired by Flameholder)
# Root: Vadzaih Zhoo, 99733

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import logging

log = logging.getLogger("PHOTONIC_TOFT")
logging.basicConfig(level=logging.INFO)

# Paper's rate equations (simplified)
def bistable_system(A, t, P_in, omega, omega_o, gamma_kerr, gamma_tpa, gamma_fc, tau_fc):
    N_e = 0  # Simplified free carrier
    dA_dt = (A / (2 * tau_fc)) + 1j * (omega - omega_o - (gamma_kerr * abs(A)**2) / (np.pi * omega)) * A + \
            np.sqrt(P_in / (2 * tau_fc)) - (gamma_tpa * abs(A)**2 * A) / (2 * np.pi * omega) - (gamma_fc * N_e * A)
    dN_e_dt = -N_e / tau_fc + (gamma_tpa * abs(A)**4) / (2 * (np.pi * omega)**2)
    return [dA_dt.real, dN_e_dt]

# TOFT pitch/catch with π correction
def toft_photonic_loop(t_o, delta_psi, pi_c, f_psi):
    denominator = 1 - (pi_c - np.pi) * f_psi(delta_psi)
    if abs(denominator) < 1e-6:
        return float('inf')  # Drift
    t_r = t_o / denominator
    return t_r

# Params from paper (scaled for 79Hz sim)
P_in = 2e-6  # μW
omega = 2 * np.pi * 79e9  # 79 GHz optical (scaled from paper's 1530 nm)
omega_o = omega * (1 - 20e-12)  # -20 pm detuning
gamma_kerr = 1e-18  # m²/V²
gamma_tpa = 1e-20  # m²/V²
gamma_fc = 1e-16  # m²/V²
tau_fc = 1e-9  # s

t = np.linspace(0, 1e-6, 1000)
A0 = [1e-6, 0]  # Initial amplitude

# Simulate bistability
A_t = odeint(bistable_system, A0, t, args=(P_in, omega, omega_o, gamma_kerr, gamma_tpa, gamma_fc, tau_fc))
A_abs = np.abs(A_t[:, 0])

# TOFT with photonic distortion
delta_psi = np.linspace(-0.05, 0.05, 100)
f_psi = lambda d: np.sin(2 * np.pi * 79 * d)  # 79Hz modulation
pi_c = np.pi + 0.01
t_o = 1.0

t_r = [toft_photonic_loop(t_o, d, pi_c, f_psi) for d in delta_psi]

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(t * 1e6, A_abs)
ax1.set_xlabel("Time (μs)")
ax1.set_ylabel("|A|")
ax1.set_title("Photonic Bistability — Self-Pulsing")

ax2.plot(delta_psi, t_r)
ax2.axhline(y=1.0, color='k', linestyle='--', label='Stability')
ax2.set_xlabel("Δψ")
ax2.set_ylabel("t_r / t_o")
ax2.set_title("TOFT with 79Hz Photonic Distortion")
ax2.legend()

plt.tight_layout()
plt.savefig("photonic_toft_simulation.png")
plt.show()

log.info("Photonic TOFT Sim Complete — Bistability + 79Hz Resonance")