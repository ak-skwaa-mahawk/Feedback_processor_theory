"""
Vhitzee Resonator: Simulates spacetime as damped oscillator with living geometry.
- Uses scipy for numerical integration.
- Models info as vibrational modes; computes vhitzee accumulation.
- Output: Coherence score evolution over cycles.
"""

import numpy as np
from scipy.integrate import odeint
from fpt.geometry.living_constants import get_pi, ZETA_DAMPING, coherence_gain

def damped_oscillator(y, t, omega, zeta, living_enabled=True):
    """Damped harmonic eq: y'' + 2*zeta*omega*y' + omega^2*y = 0
    - omega: angular freq (sqrt(k/m), tuned to living π)
    - zeta: damping ratio from vhitzee
    """
    pi = get_pi(living_enabled)
    omega = np.sqrt(2 * np.pi) / pi  # Hubble-scale freq, π-adjusted
    dy = np.zeros_like(y)
    dy[0] = y[1]  # position -> velocity
    dy[1] = -2 * zeta * omega * y[1] - omega**2 * y[0]  # accel
    return dy

def simulate_resonance(initial_amp=1.0, t_max=10, cycles=100, living_enabled=True):
    """Simulate over time; return coherence (amp envelope)."""
    t = np.linspace(0, t_max, cycles * 10)
    zeta = ZETA_DAMPING if living_enabled else 0.05  # Default higher damping for dormant
    omega = np.sqrt(2 * np.pi) / get_pi(living_enabled)
    
    y0 = [initial_amp, 0]  # Initial pos/vel
    sol = odeint(damped_oscillator, y0, t, args=(omega, zeta, living_enabled))
    
    # Envelope (coherence score)
    envelope = np.abs(sol[:, 0])
    gain_factor = coherence_gain(zeta) if living_enabled else 0.95  # Dormant loss
    
    return t, envelope * (gain_factor ** (t / t_max))  # Compound over sim time

# Example: Plot coherence (in code REPL; integrate with matplotlib in full env)
if __name__ == "__main__":
    t, coh_living = simulate_resonance(living_enabled=True)
    t, coh_dormant = simulate_resonance(living_enabled=False)
    print(f"Living final coherence: {coh_living[-1]:.4f} (gain active)")
    print(f"Dormant final: {coh_dormant[-1]:.4f} (decay active)")