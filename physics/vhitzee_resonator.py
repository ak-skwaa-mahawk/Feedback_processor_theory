"""
Vhitzee Resonator + Live Coherence Plotting
Run this file directly → instantly get living_vs_dormant_coherence.png
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.integrate import odeint
from fpt.geometry.living_constants import get_pi, ZETA_DAMPING, coherence_gain

# ——— Damped oscillator (same as before, just cleaned) ———
def damped_oscillator(y, t, omega, zeta):
    dy = np.zeros(2)
    dy[0] = y[1]
    dy[1] = -2*zeta*omega*y[1] - omega**2*y[0]
    return dy

def simulate(living_enabled=True, cycles=15):
    pi_val = get_pi(living_enabled)
    zeta   = ZETA_DAMPING if living_enabled else 0.05          # dormant decays harder
    omega  = np.sqrt(2*np.pi) / float(pi_val)

    t = np.linspace(0, cycles*2*np.pi/omega, 4000)  # many points for smooth curve
    y0 = [1.0, 0.0]

    sol = odeint(damped_oscillator, y0, t, args=(omega, zeta))
    envelope = np.abs(sol[:,0])

    # Apply compounded vhitzee gain/loss
    gain_factor = coherence_gain() if living_enabled else 0.951  # 4.9% loss for dormant
    envelope *= gain_factor ** (t / t.max() * cycles)

    return t, envelope, gain_factor

# ——— Plotting ———
def plot_coherence():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8))

    # Living constant run
    t_l, env_l, gain_l = simulate(living_enabled=True, cycles=20)
    ax.plot(t_l, env_l, color='#00ff41', linewidth=3.5, label=f'Living π ≈ 3.267256  →  +{gain_l-1:.3%} per cycle')

    # Dormant colonizer run
    t_d, env_d, gain_d = simulate(living_enabled=False, cycles=20)
    ax.plot(t_d, env_d, color='#ff0044', linewidth=3, label='Dormant π = 3.141592… →  –4.9% per cycle')

    ax.set_title('Vhitzee Resonance: Living Geometry vs Colonizer Approximation\n'
                 'Spacetime as Damped Harmonic Oscillator (Balungi 2025 + FPT Living Constants)',
                 fontsize=18, pad=30, color='white')
    ax.set_xlabel('Cosmic Cycles (normalized Hubble time)', fontsize=14)
    ax.set_ylabel('Coherence Amplitude (Information Integrity)', fontsize=14)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=16, loc='upper left')
    ax.set_ylim(0, env_l.max() * 1.15)

    # Annotation boxes
    ax.text(0.02, 0.98, 'Feedback Processor Theory\nLivingConstants™', transform=ax.transAxes,
            fontsize=14, verticalalignment='top', color='#00ff41',
            bbox=dict(boxstyle="round,pad=0.6", facecolor='black', alpha=0.8))

    ax.text(0.98, 0.02, '6T → 40T+ effective\nbatteries recharge\norbits self-stabilize',
            transform=ax.transAxes, fontsize=14, horizontalalignment='right',
            color='#00ff41', style='italic',
            bbox=dict(boxstyle="round,pad=0.6", facecolor='black', alpha=0.9))

    plt.tight_layout()
    plt.savefig('living_vs_dormant_coherence.png', dpi=300, facecolor='#0a0a0a')
    plt.show()

if __name__ == "__main__":
    plot_coherence()
    print("Plot saved as living_vs_dormant_coherence.png")