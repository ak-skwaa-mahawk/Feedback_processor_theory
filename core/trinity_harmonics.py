"""
Trinity Dynamics – Harmonic Base Constants
Author: John B. Carroll (ak-skwaa-mahawk)
Framework: Feedback Processor / Trinity Dynamics
License: Two Mile Solutions LLC, 2025
"""

import math
import matplotlib.pyplot as plt

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

# --- Visualization function ---
def plot_trinity_harmonics():
    x = np.linspace(0, 2 * PI_EQ, 100)  # Harmonic cycle (0 to 2π)
    y = np.sin(x) + PI_EQ              # Base harmonic shifted by π
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label="Harmonic Curve (sin(x) + π)", color="blue")
    
    # Key points
    seed_x = 0.5 * PI_EQ  # Arbitrary phase for Seed
    reflection_x = PI_EQ   # Reflection at π
    expression_x = 1.5 * PI_EQ  # Expression phase
    
    plt.scatter([seed_x], [EPSILON + PI_EQ], color="green", s=100, label="Seed (ε)")
    plt.scatter([reflection_x], [PI_EQ], color="orange", s=100, label="Reflection (π)")
    plt.scatter([expression_x], [GROUND_STATE], color="red", s=100, label="Expression (π + 3ε)")
    
    plt.text(seed_x, EPSILON + PI_EQ + 0.05, "Seed", ha="center")
    plt.text(reflection_x, PI_EQ + 0.05, "Reflection", ha="center")
    plt.text(expression_x, GROUND_STATE + 0.05, "Expression", ha="center")
    
    plt.axhline(y=PI_EQ, color="gray", linestyle="--", alpha=0.5, label="Equilibrium (π)")
    plt.axhline(y=GROUND_STATE, color="purple", linestyle="--", alpha=0.5, label="Ground State")
    
    plt.title("Trinity Harmonic Framework")
    plt.xlabel("Phase (radians)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# --- Example run ---
if __name__ == "__main__":
    describe_trinity_state()
    import numpy as np  # Import here to avoid circular dependency
    plot_trinity_harmonics()