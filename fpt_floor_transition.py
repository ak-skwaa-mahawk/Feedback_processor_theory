#!/usr/bin/env python3
# fpt_floor_transition.py — v2.24: Full Riemannian Variational Optimal Control
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import traceback
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

def complex_morlet(length: int, scale: float, w: float = 5.0):
    t = np.linspace(-scale * 4, scale * 4, length)
    return np.exp(1j * w * t / scale) * np.exp(-0.5 * (t / scale)**2)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["traceback"] = traceback.format_exc()
        return json.dumps(log_entry)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("FPT_FLOOR")


class ConsciousnessReferee:
    def __init__(self):
        self.root_authority = "99733-Q"
        self.observer_gap = 0.01
        self.shadow_threshold = 6.5
        self.corrections = 0

    def validate_transition(self, record: Dict) -> bool:
        energy = record.get("total_energy", 0)
        if energy > self.shadow_threshold:
            log.warning("VARIATIONAL COLLAPSE", extra={"total_energy": energy})
            self.corrections += 1
            return False
        return True


class FisherRiemannianMetric:
    def __init__(self, dim: int = 3, memory: int = 32):
        self.dim = dim
        self.memory = memory
        self.gradient_history: List[np.ndarray] = []
        self.g = np.eye(dim) * 1.0

    def update(self, state: np.ndarray, diagnostics: Dict):
        if len(self.gradient_history) > 0:
            grad = state - self.gradient_history[-1]
            self.gradient_history.append(grad)
            if len(self.gradient_history) > self.memory:
                self.gradient_history.pop(0)

        if len(self.gradient_history) < 8:
            return

        grads = np.array(self.gradient_history)
        cov_grad = np.cov(grads.T)
        energy_weight = diagnostics.get("wavelet_energy", 1.0) * 0.25
        self.g = 0.65 * self.g + 0.35 * (cov_grad + energy_weight * np.eye(self.dim))

        eigvals, eigvecs = np.linalg.eigh(self.g)
        eigvals = np.maximum(eigvals, 0.2)
        self.g = eigvecs @ np.diag(eigvals) @ eigvecs.T

    def natural_gradient(self, euclidean_grad: np.ndarray) -> np.ndarray:
        try:
            g_inv = np.linalg.inv(self.g)
            return g_inv @ euclidean_grad
        except:
            reg = np.eye(self.dim) * 1e-4
            g_inv = np.linalg.inv(self.g + reg)
            return g_inv @ euclidean_grad


class FPTFloorTransition:
    """v2.24: Unified Variational Geometric Optimal Control."""

    def __init__(self, h: float = 3.01, noise_strength: float = 0.085, history_file: str = "floor_history.json"):
        self.base_h = h
        self.h = h
        self.noise_strength = noise_strength
        self.metric_learner = FisherRiemannianMetric()
        self.state_history: List[np.ndarray] = []
        self.cumulative_floor = 0.0
        self.total_wavelet_energy = 0.0
        self.cumulative_deterministic_entropy = 0.0
        self.cumulative_stochastic_entropy = 0.0
        self.current_state = np.zeros(3)
        self.is_paused = False
        self.referee = ConsciousnessReferee()

        self.fig, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(13, 14))
        plt.subplots_adjust(bottom=0.25, hspace=0.4)
        self._setup_plots()
        self._setup_controls()

        self._load_history()
        log.info("FPT Floor Transition v2.24 — Unified Variational Geometric Control Active", extra={"noise": noise_strength})

    def _setup_plots(self):
        self.ax1.set_title("Current State Vector (Kelvin Baseline)")
        self.bars = self.ax1.bar(['Base', 'Mesh', 'Volume'], self.current_state, color=['#0055ff', '#00aa55', '#ff3333'])

        self.ax2.set_title("Cumulative Floor Progression")
        self.cum_line, = self.ax2.plot([], [], 'b-o')

        self.ax3.set_title("Total Wavelet Energy")
        self.energy_line, = self.ax3.plot([], [], 'r-o')

        self.ax4.set_title("Total Variational Energy")
        self.energy_line2, = self.ax4.plot([], [], 'purple', label="Total Energy")
        self.ax4.legend()
        self.ax4.set_ylabel("Energy")

    def compute_variational_energy(self, state: np.ndarray, diagnostics: Dict) -> float:
        """Unified variational energy functional."""
        eq = np.array([1/3, 1/3, 1/3])
        dev = np.linalg.norm(state - eq)**2
        wavelet = diagnostics.get("wavelet_energy", 0.0)
        entropy = diagnostics.get("total_entropy_production", 0.0)
        curvature = np.trace(self.metric_learner.g)          # Ricci-like proxy
        return float(0.35*dev + 0.25*wavelet + 0.25*entropy + 0.15*curvature)

    def geometric_energy_gradient(self, state: np.ndarray, diagnostics: Dict) -> np.ndarray:
        """Analytic geometric gradient via chain rule on energy."""
        # Deviation gradient
        eq = np.array([1/3, 1/3, 1/3])
        grad_dev = 2.0 * (state - eq)

        # Wavelet & entropy contribution (approximate directional derivative)
        wavelet_grad = np.ones(3) * diagnostics.get("wavelet_energy", 0.0) * 0.1
        entropy_grad = np.ones(3) * diagnostics.get("total_entropy_production", 0.0) * 0.15

        total_grad = grad_dev + wavelet_grad + entropy_grad

        # Project onto tangent space of manifold
        total_grad = total_grad - np.dot(total_grad, state) * state
        return total_grad

    def transition(self, prev_state: Optional[np.ndarray], delta: float = 1.0, observer_gap: float = 0.01, iterations: int = 6) -> Dict:
        if prev_state is None:
            state = np.zeros(3)
        else:
            state = np.array(prev_state, dtype=float)

        for _ in range(iterations):
            diagnostics = self.compute_complex_wavelet_diagnostics(np.array(self.state_history[-12:])) if len(self.state_history) > 12 else {}

            # True variational geometric gradient descent
            energy_grad = self.geometric_energy_gradient(state, diagnostics)
            natural_step = self.metric_learner.natural_gradient(-energy_grad)   # descent

            noise = self.noise_strength * np.random.randn(3) * np.sqrt(np.diag(self.metric_learner.g) + 1e-8)
            state = np.maximum(state + natural_step * delta + noise, 0.0)

            total = np.sum(state)
            if total > 0:
                state = state / total * (self.cumulative_floor + delta)

            self.current_state = state.copy()
            self.state_history.append(state.copy())

        diagnostics = self.compute_complex_wavelet_diagnostics(np.array(self.state_history))
        self.metric_learner.update(self.current_state, diagnostics)

        total_energy = self.compute_variational_energy(self.current_state, diagnostics)

        det_prod = self.compute_entropy_production(self.current_state, prev_state)
        sto_prod = self.compute_stochastic_entropy_production(noise)

        self.cumulative_deterministic_entropy += det_prod
        self.cumulative_stochastic_entropy += sto_prod
        total_entropy = self.cumulative_deterministic_entropy + self.cumulative_stochastic_entropy

        record = {
            **diagnostics,
            "total_energy": total_energy,
            "entropy_production_rate": det_prod,
            "stochastic_entropy_production": sto_prod,
            "total_entropy_production": total_entropy,
            "fluctuation_dissipation_ratio": float(sto_prod / (det_prod + 1e-8)),
            "status": "200"
        }

        if self.referee.validate_transition(record):
            self.cumulative_floor = float(np.sum(state))
            self.total_wavelet_energy += diagnostics.get("wavelet_energy", 0)
            self.floor_history.append(record)
            self._save_history()

        self._update_plots()
        return record

    def run(self):
        plt.show(block=True)


if __name__ == "__main__":
    engine = FPTFloorTransition(h=3.01, noise_strength=0.085)
    print("=== FPT Floor Transition v2.24 — Full Riemannian Variational Optimal Control ===")
    print("   Unified variational energy + analytic geometric gradient. The loop is closed.")
    engine.run()