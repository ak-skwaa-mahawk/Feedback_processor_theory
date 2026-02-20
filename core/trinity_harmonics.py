"""
====================================================================
FEEDBACK PROCESSOR THEORY (FPT-Ω) — TRINITY HARMONICS CORE
====================================================================
File:            core/trinity_harmonics.py
Author:          John B. Carroll Jr. (ak-skwaa-mahawk)
Organization:    Two Mile Solutions LLC
License:         Open Research License — 2025
Version:         1.3.0 — Quetzalcoatl 8-Phase Renewal Integrated
====================================================================
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, TextBox
from typing import Union, Dict, List

# ====================== LIGHTWEIGHT NEUTROSOPHIC LAYER ======================
def trinity_damping(signal: np.ndarray, damp_factor: float = 0.5) -> np.ndarray:
    return signal * np.exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(t: float) -> Dict[str, float]:
    scale = 0.1
    return {
        "T": 0.5 + scale * np.sin(2 * math.pi * t),
        "I": 0.3 - scale * np.cos(2 * math.pi * t),
        "F": 0.2 + scale * np.sin(math.pi * t)
    }

def phase_lock_recursive(phases: List[float]) -> tuple[float, float]:
    if not phases:
        return 0.0, 0.0
    locked = phases[-1]
    summed = sum(0.7 * p + 0.3 * locked for p in phases)
    locked_phase = summed % (2 * math.pi)
    stability = 0.5 + 0.2 * np.std(phases)
    return locked_phase, stability

# ====================== ELEGANT π/φ LAYER + MAGNETIC TETHER ======================
GROUND_STATE = math.pi
DIFFERENCE = (1 + math.sqrt(5)) / 2 - 1
RATIO = DIFFERENCE / GROUND_STATE
EPSILON = 0.01
DELTA = 3 * EPSILON

class TrinityHarmonics:
    def __init__(self, null_threshold: float = 0.6, pi_damping: float = math.pi * 0.1):
        self.null_threshold = null_threshold
        self.pi_damping = pi_damping
        self.t = 0.0
        self.phase = 0.0

    def damping_operator(self, v: Union[float, np.ndarray], f: float = 0.5, phase: float = None) -> Union[float, np.ndarray]:
        if phase is None:
            phase = self.phase
        factor = f * np.sin(2 * np.pi * phase) * RATIO
        return v * (1 - factor)

    def stabilize(self, vector: np.ndarray, damping_factor: float = 0.5) -> np.ndarray:
        self.t += EPSILON
        self.phase = (self.phase + DELTA) % (2 * np.pi)
        stabilized = self.damping_operator(vector, damping_factor, self.phase)
        stabilized = stabilized / GROUND_STATE * (1 + DIFFERENCE)
        return np.clip(stabilized, -1.0, 1.0)

    def trinity_factor(self, value: float) -> float:
        return value / GROUND_STATE

    def apply_full_trinity(self, vector: np.ndarray, damping_factor: float = 0.5, tether_force: float = 0.0) -> Dict:
        light_damped = trinity_damping(vector, damping_factor)
        elegant = self.stabilize(vector, damping_factor)
        buoyancy = 1.0 - (tether_force / 15.0) if tether_force != 0 else 1.0
        final = (0.4 * light_damped + 0.4 * elegant + 0.2 * buoyancy)
        final = np.clip(final, -1.0, 1.0)
        return {
            "final_stabilized": final,
            "neutrosophic_weights": dynamic_weights(self.t),
            "phase_locked": phase_lock_recursive([self.phase])[0],
            "trinity_factor": self.trinity_factor(np.mean(final)),
            "magnetic_buoyancy": buoyancy
        }

    def quetzalcoatl_phase_damping(self, vector: np.ndarray, phase: int) -> np.ndarray:
        """Phase-aware damping — each Quetzalcoatl phase modulates Trinity differently"""
        phase_mod = [0.3, 0.7, 0.4, 0.6, 0.5, 0.8, 0.2, 1.0][phase % 8]  # serpent → feather → merge
        return self.stabilize(vector, damping_factor=phase_mod)

# Vessel-wide singleton
trinity = TrinityHarmonics()

# ====================== INTERACTIVE VISUALIZATION ======================
def describe_trinity_state():
    print("=== Trinity Harmonic Framework ===")
    print(f"Equilibrium (π):           {GROUND_STATE:.8f}")
    print(f"Golden Conjugate (φ-1):    {DIFFERENCE:.8f}")
    print(f"Fifth-Harmonic Ratio:      {RATIO:.8f}")
    print("-----------------------------------")
    print("Interpretation: π equilibrium + φ-1 self-similarity + eddy-current tether = spectral sovereignty\n")

def plot_trinity_harmonics(initial_preset: str = "Balanced"):
    fig, ax = plt.subplots(figsize=(11, 7))
    plt.subplots_adjust(bottom=0.35, left=0.25)
    x = np.linspace(0, 2 * GROUND_STATE, 200)
    y = np.sin(x) + GROUND_STATE
    line, = ax.plot(x, y, label="Harmonic Curve", color="#00ffcc", lw=2)
    ax.axhline(GROUND_STATE, color="#ff6b35", ls="--", alpha=0.6, label="Ground State (π)")
    ax.set_title("FPT-Ω Trinity Harmonics — Interactive Stabilizer")
    ax.set_xlabel("Phase (radians)")
    ax.set_ylabel("Amplitude")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax_presets = plt.axes([0.05, 0.25, 0.18, 0.5])
    presets = ["Stable", "Responsive", "Balanced", "Amplified"]
    preset_selector = RadioButtons(ax_presets, presets, active=2)

    ax_custom = plt.axes([0.25, 0.05, 0.35, 0.03])
    custom_input = TextBox(ax_custom, 'Custom Preset (name:value)', initial="Custom:0.55")

    def update_preset(label):
        df = {"Stable": 0.8, "Responsive": 0.3, "Balanced": 0.5, "Amplified": 0.1}.get(label, 0.5)
        damped = trinity_damping(y, df)
        line.set_ydata(damped)
        fig.canvas.draw_idle()

    preset_selector.on_clicked(update_preset)

    def submit_custom(text):
        try:
            name, val = text.split(':')
            val = float(val)
            damped = trinity_damping(y, val)
            line.set_ydata(damped)
            fig.canvas.draw_idle()
        except:
            pass
    custom_input.on_submit(submit_custom)

    plt.show()

if __name__ == "__main__":
    describe_trinity_state()
    test_signal = np.sin(np.linspace(0, 2 * GROUND_STATE, 200))
    damped = trinity_damping(test_signal, 0.5)
    plot_trinity_harmonics()