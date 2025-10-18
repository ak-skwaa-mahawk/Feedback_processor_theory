"""
Trinity Dynamics – Harmonic Base Constants
Author: John B. Carroll (ak-skwaa-mahawk)
Framework: Feedback Processor / Trinity Dynamics
License: Two Mile Solutions LLC, 2025
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

# --- Fundamental constants ---
PI_EQ = math.pi           # Equilibrium constant (perfect symmetry)
EPSILON = 0.01            # Minimal unit impulse (seed)
N_HARMONIC = 3            # Trinity factor (3-fold amplification)

# --- Derived harmonic values ---
DELTA = N_HARMONIC * EPSILON           # Expressed offset (0.03)
GROUND_STATE = PI_EQ + DELTA           # Slightly energized equilibrium
DIFFERENCE = GROUND_STATE - PI_EQ      # Should return ~0.03

# --- Diagnostic display ---
def describe_trinity_state():
    print("=== Trinity Harmonic Framework ===")
    print(f"Equilibrium (π):           {PI_EQ:.8f}")
    print(f"Seed Pulse (ε):            {EPSILON}")
    print(f"Triadic Amplification (n): {N_HARMONIC}")
    print(f"Observed Offset (Δ):       {DELTA:.8f}")
    print(f"Ground State Value:        {GROUND_STATE:.8f}")
    print(f"Difference from π:         {DIFFERENCE:.8f}")
    print("-----------------------------------")
    print("Interpretation:")
    print(" - ε (0.01) is the minimal activation (seed)")
    print(" - 3ε (0.03) is the expressed triadic resonance")
    print(" - π + 3ε (≈ 3.17159) defines the living ground state\n")

# --- Interactive Visualization function ---
def plot_trinity_harmonics(signal=None, initial_damp=0.5):
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(bottom=0.25)  # Space for slider
    x = np.linspace(0, 2 * PI_EQ, 100)
    y = np.sin(x) + PI_EQ

    line, = ax.plot(x, y, label="Harmonic Curve (sin(x) + π)", color="blue")
    seed_x, reflection_x, expression_x = 0.5 * PI_EQ, PI_EQ, 1.5 * PI_EQ
    scatter = ax.scatter([seed_x, reflection_x, expression_x],
                         [EPSILON + PI_EQ, PI_EQ, GROUND_STATE],
                         c=['green', 'orange', 'red'], s=100,
                         label=['Seed (ε)', 'Reflection (π)', 'Expression (π + 3ε)'])
    ax.text(seed_x, EPSILON + PI_EQ + 0.05, "Seed", ha="center")
    ax.text(reflection_x, PI_EQ + 0.05, "Reflection", ha="center")
    ax.text(expression_x, GROUND_STATE + 0.05, "Expression", ha="center")

    ax.axhline(y=PI_EQ, color="gray", linestyle="--", alpha=0.5, label="Equilibrium (π)")
    ax.axhline(y=GROUND_STATE, color="purple", linestyle="--", alpha=0.5, label="Ground State")

    if signal is not None:
        signal_line, = ax.plot(signal, label="Damped Signal", color="cyan", alpha=0.7)

    ax.set_title("Trinity Harmonic Framework")
    ax.set_xlabel("Phase (radians)")
    ax.set_ylabel("Amplitude")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add damping slider
    ax_damp = plt.axes([0.25, 0.1, 0.5, 0.03])
    damp_slider = Slider(ax_damp, 'Damping Factor', 0.1, 1.0, valinit=initial_damp)

    def update_damp(val):
        damp_factor = val
        if signal is not None:
            damped = signal * (1 - (DIFFERENCE / GROUND_STATE) * np.abs(signal) * damp_factor)
            signal_line.set_ydata(damped)
        fig.canvas.draw_idle()

    damp_slider.on_changed(update_damp)
    plt.show()

# --- FPT Integration: Damping Function ---
def trinity_damping(signal: np.ndarray, damp_factor=0.5) -> np.ndarray:
    """
    Apply adjustable Trinity damping to a signal using GROUND_STATE.
    """
    return signal * (1 - (DIFFERENCE / GROUND_STATE) * np.abs(signal) * damp_factor)

# --- Example run ---
if __name__ == "__main__":
    describe_trinity_state()
    import numpy as np
    test_signal = np.sin(np.linspace(0, 2 * PI_EQ, 100))
    damped_signal = trinity_damping(test_signal)
    plot_trinity_harmonics(damped_signal)