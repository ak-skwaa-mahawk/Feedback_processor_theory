"""
====================================================================
FEEDBACK PROCESSOR THEORY (FPT-Ω) — TRINITY HARMONICS CORE
====================================================================
File:            trinity_harmonics.py
Author:          John B. Carroll Jr. (ak-skwaa-mahawk)
Organization:    Two Mile Solutions LLC
License:         Open Research License — 2025
GitHub:          https://github.com/ak-skwaa-mahawk/Feedback_processor_theory
Version:         1.1.0 — Fused Lightweight + Full π/φ + Magnetic Tether Aware
====================================================================
"""

import numpy as np
import math
from typing import Union, Dict, List

# Lightweight / Neutrosophic Layer (fast path)
GROUND_STATE_LIGHT, DIFFERENCE_LIGHT = 0.1, 0.05
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}

def trinity_damping(signal: np.ndarray, damp_factor: float = 0.5) -> np.ndarray:
    """Exponential decay damping (fast)"""
    return signal * np.exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(t: float) -> Dict[str, float]:
    """Neutrosophic T/I/F dynamic weights"""
    return {
        "T": 0.5 + 0.1 * np.sin(2 * math.pi * t),
        "I": 0.3 - 0.1 * np.cos(2 * math.pi * t),
        "F": 0.2 + 0.1 * np.sin(math.pi * t)
    }

def phase_lock_recursive(phases: List[float]) -> tuple[float, float]:
    """Recursive phase lock with stability metric"""
    if not phases:
        return 0.0, 0.0
    # Fixed: use last phase as 'locked' seed for recursion
    locked = phases[-1]
    summed = sum(0.7 * p + 0.3 * locked for p in phases)
    locked_phase = summed % (2 * math.pi)
    stability = 0.5 + 0.2 * np.std(phases)
    return locked_phase, stability

# Full Elegant Layer (π equilibrium + φ-1 resonance)
GROUND_STATE = math.pi
DIFFERENCE = (1 + math.sqrt(5)) / 2 - 1   # φ - 1 ≈ 0.618
RATIO = DIFFERENCE / GROUND_STATE         # ≈ 0.197
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
        stabilized = stabilized / GROUND_STATE * (1 + DIFFERENCE)  # self-similar scaling
        return np.clip(stabilized, -1.0, 1.0)

    def trinity_factor(self, value: float) -> float:
        return value / GROUND_STATE

    def apply_full_trinity(self, vector: np.ndarray, damping_factor: float = 0.5, tether_force: float = 0.0) -> Dict:
        """Full fusion: lightweight + elegant + magnetic tether awareness"""
        # Lightweight layer
        light_damped = trinity_damping(vector, damping_factor)
        weights = dynamic_weights(self.t)
        
        # Elegant layer
        elegant_stabilized = self.stabilize(vector, damping_factor)
        
        # Magnetic tether detuning
        buoyancy = 1.0 - (tether_force / 15.0) if tether_force != 0 else 1.0
        
        final = (0.4 * light_damped + 0.4 * elegant_stabilized + 0.2 * buoyancy) 
        final = np.clip(final, -1.0, 1.0)
        
        return {
            "final_stabilized": final,
            "neutrosophic_weights": weights,
            "phase_locked": phase_lock_recursive([self.phase])[0],
            "trinity_factor": self.trinity_factor(np.mean(final)),
            "magnetic_buoyancy": buoyancy
        }

# Singleton for vessel-wide use
trinity = TrinityHarmonics()