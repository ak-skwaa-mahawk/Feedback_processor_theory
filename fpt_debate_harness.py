#!/usr/bin/env python3
# fpt_debate_harness.py — v1.0: Multi-Agent Asymmetric Debate Sandbox
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import logging
import matplotlib
matplotlib.use('TkAgg' if matplotlib.get_backend() != 'agg' else 'agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Setup basic structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("FPT_DEBATE")

class DebateAgent:
    """An independent FPT engine instance acting as a debate participant."""
    def __init__(self, name: str, h_factor: float, stance_offset: float):
        self.name = name
        self.h = h_factor
        self.stance_offset = stance_offset # Individual metabolic bias
        self.state = np.array([1.0, 0.0, 0.0], dtype=float)
        self.history: List[List[float]] = [self.state.tolist()]

    def process_statement(self, incoming_vector: np.ndarray, delta: float) -> np.ndarray:
        """Absorbs an opponent's point, applies internal h-gears, and projects a counter-argument."""
        # Mix incoming perspective with current state matrix
        mixed_base = (self.state * 0.4) + (incoming_vector * 0.6)
        
        # 'Take 2, Leave 1' asymmetric transformation adjusted by stance factor
        take = 2.0 * (1.0 / (self.h + self.stance_offset))
        leave = 1.0 / (self.h - self.stance_offset)
        
        step_mod = np.array([-take, take - leave, leave], dtype=float)
        updated_state = np.maximum(mixed_base + step_mod * delta, 0.0)
        
        # Conserve the local logical floor baseline
        total = np.sum(updated_state)
        if total > 0:
            updated_state = (updated_state / total) * (np.sum(self.state) + delta)
            
        self.state = updated_state.copy()
        self.history.append(self.state.tolist())
        return self.state

class StructuralReferee:
    """Monitors information loss, shadow accumulation, and locks system boundaries."""
    def __init__(self, threshold: float = 0.8):
        self.authority = "99733-Q"
        self.threshold = threshold
        self.entropy_ledger: List[float] = []

    def evaluate_clash(self, v1: np.ndarray, v2: np.ndarray) -> Tuple[float, bool]:
        """Calculates the distance (shadow divergence) between opposing worldviews."""
        shadow_divergence = float(np.linalg.norm(v1 - v2))
        self.entropy_ledger.append(shadow_divergence)
        
        # True means the debate is healthy and expanding; False means flat loop deadlock
        is_healthy = shadow_divergence > self.threshold
        return shadow_divergence, is_healthy

class FPTDebateSandbox:
    """The formal environment managing agent runtime collisions and live visualization."""
    def __init__(self):
        # Initialize Agent Einstein vs Agent NonBeliever
        self.agent_a = DebateAgent("Einstein (Generative)", h_factor=3.173, stance_offset=0.05)
        self.agent_b = DebateAgent("NonBeliever (Extractive)", h_factor=2.945, stance_offset=-0.05)
        self.referee = StructuralReferee(threshold=0.5)
        
        self.step_count = 0
        self.is_paused = False
        
        # Graphical Layout Setup
        self.fig, (self.ax_states, self.ax_shadow) = plt.subplots(2, 1, figsize=(11, 8))
        plt.subplots_adjust(bottom=0.2, hspace=0.4)
        
        self._setup_plots()
        self._setup_controls()
        
    def _setup_plots(self):
        self.ax_states.set_title("Dimensional Argument Space (1D Need → 2D Mesh → 3D Volume)")
        self.ax_states.set_ylabel("Vector Magnitude")
        
        x = np.arange(3)
        self.bar_width = 0.35
        
        self.bars_a = self.ax_states.bar(x - self.bar_width/2, self.agent_a.state, self.bar_width, label=self.agent_a.name, color='#0055ff')
        self.bars_b = self.ax_states.bar(x + self.bar_width/2, self.agent_b.state, self.bar_width, label=self.agent_b.name, color='#ff3333')
        
        self.ax_states.set_xticks(x)
        self.ax_states.set_xticklabels(['1D Base', '2D Mesh', '3D Volume'])
        self.ax_states.set_ylim(0, 7)
        self.ax_states.legend()
        
        self.ax_shadow.set_title("Referee Metric: Shadow Divergence History (Structural Evolution)")
        self.ax_shadow.set_ylabel("Divergence")
        self.shadow_line, = self.ax_shadow.plot([], [], '#aa00ff', marker='o', markersize=4)
        
    def _setup_controls(self):
        ax_next = plt.axes([0.42, 0.05, 0.15, 0.05])
        self.btn_next = Button(ax_next, 'Execute Clash Cycle')
        self.btn_next.on_clicked(self._cycle_step)
        
    def _cycle_step(self, event):
        self.step_count += 1
        delta_tick = 1.0
        
        # Cross-pollinate state vectors through the asymmetric engines
        vec_a_next = self.agent_a.process_statement(self.agent_b.state, delta_tick)
        vec_b_next = self.agent_b.process_statement(self.agent_a.state, delta_tick)
        
        # Referee intercepts the metrics to score boundary health
        divergence, healthy = self.referee.evaluate_clash(vec_a_next, vec_b_next)
        
        log.info(f"Cycle {self.step_count} Executed | Divergence: {divergence:.4f} | Health Status: {healthy}")
        
        if not healthy:
            log.warning(f"CRITICAL FLAT LOCK DETECTED — Authority {self.referee.authority} injecting variance.")
            # Inject a raw structural floor boost to break the ego mirror loop
            self.agent_a.state += 0.317
            self.agent_b.state += 0.104
            
        self._update_plots()
        
    def _update_plots(self):
        for bar, val in zip(self.bars_a, self.agent_a.state):
            bar.set_height(val)
        for bar, val in zip(self.bars_b, self.agent_b.state):
            bar.set_height(val)
            
        self.shadow_line.set_data(range(len(self.referee.entropy_ledger)), self.referee.entropy_ledger)
        self.ax_shadow.relim()
        self.ax_shadow.autoscale_view()
        
        self.fig.canvas.draw_idle()

    def run(self):
        plt.show()

if __name__ == "__main__":
    sandbox = FPTDebateSandbox()
    sandbox.run()
