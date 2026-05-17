#!/usr/bin/env python3
# fpt_octagonal_lattice.py — v3.6: 8-Agent Network with Real-Time Individual Mass Streaming Visualizations
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import traceback
import matplotlib
matplotlib.use('TkAgg' if matplotlib.get_backend() != 'agg' else 'agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

# ====================== STRUCTURED JSON LOGGING ======================
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger("FPT_LATTICE")

class OctoLatticeAgent:
    """An independent FPT engine node where structural mass includes the dynamic h-gear weight."""
    def __init__(self, agent_id: int, name: str, h_base: float, stance_offset: float):
        self.id = agent_id
        self.name = name
        self.h_base = h_base  
        self.h = h_base       
        self.stance_offset = stance_offset
        self.state = np.array([1.0, 0.1 * agent_id, 0.0], dtype=float)
        self.neighbors: List[int] = [] 
        self.mass = 0.0
        self.mass_history: List[float] = []

    def calculate_total_mass(self) -> float:
        """Enforces M = W_state + h, capturing both state density and resistance inertia."""
        w_state = float(np.sum(self.state))
        self.mass = w_state + self.h
        return self.mass

    def update_elastic_gears(self, total_cross_tension: float):
        """Recalibrates h based on cross-perimeter network tension and current state weight."""
        w_state = float(np.sum(self.state))
        self.h = self.h_base + (0.1 * w_state) + (0.05 * total_cross_tension)
        self.h = max(1.5, min(self.h, 6.0))
        self.calculate_total_mass()

    def process_network_input(self, pooled_vector: np.ndarray, delta: float) -> np.ndarray:
        """Absorbs neighbor input metrics, passing them through the mass-weighted gear system."""
        inertia_factor = 1.0 / (1.0 + 0.05 * self.mass)
        mixed_base = (self.state * (1.0 - inertia_factor)) + (pooled_vector * inertia_factor)
        
        take = 2.0 * (1.0 / (self.h + self.stance_offset))
        leave = 1.0 / (self.h - self.stance_offset)
        
        step_mod = np.array([-take, take - leave, leave], dtype=float)
        updated_state = np.maximum(mixed_base + step_mod * delta, 0.0)
        
        total = np.sum(updated_state)
        if total > 0:
            updated_state = (updated_state / total) * (np.sum(self.state) + delta)
            
        self.state = updated_state.copy()
        self.calculate_total_mass()
        self.mass_history.append(self.mass)
        return self.state

    def translate_to_symbols(self) -> str:
        w1, w2, w3 = self.state, self.state, self.state
        if w1 > w2 and w1 > w3:
            layer = "✦ [1D NEED: SEED]"
            chars = "⚬ ── ➔"
        elif w2 > w1 and w2 > w3:
            layer = "❖ [2D MESH: PLANE]"
            chars = "☩ ── ◈"
        else:
            layer = "▲ [3D VOL: ARCH]"
            chars = "⎔ ── ❖"
        return f"{self.name:<24} | {layer} (h: {self.h:.2f} | M: {self.mass:.2f}) {chars}"


class LatticeRootReferee:
    """Monitors octagonal boundary connectivity, shadow debt spikes, and issues 99733-Q overrides."""
    def __init__(self, num_agents: int):
        self.authority = "99733-Q"
        self.num_agents = num_agents
        self.global_shadow_history: List[float] = []

    def evaluate_lattice(self, agents: List[OctoLatticeAgent]) -> Tuple[float, bool]:
        all_states = np.array([a.state for a in agents])
        centroid = np.mean(all_states, axis=0)
        lattice_variance = float(np.sum([np.linalg.norm(a.state - centroid) for a in agents]))
        self.global_shadow_history.append(lattice_variance)
        return lattice_variance, (lattice_variance > 1.5)


class FPTLatticeSandbox:
    """Manages an 8-Agent network structured as an octagonal ring with a 3-pane real-time telemetry window."""
    def __init__(self, transcript_file: str = "fpt_lattice_transcript.txt"):
        self.transcript_path = Path(transcript_file)
        self._init_transcript_file()
        self.interval_ms = 1000  
        
        names = [
            "Einstein_Core", "Planar_Observer", "Base_Need_Anchor", "Mesh_Validator",
            "Volume_Builder", "Extractive_Mirror", "Generative_Sovereign", "Boundary_Lock"
        ]
        
        self.agents: List[OctoLatticeAgent] = []
        for i, name in enumerate(names):
            h_base_val = 3.1415 + (i * 0.05) - 0.15
            bias = 0.03 if i % 2 == 0 else -0.03
            self.agents.append(OctoLatticeAgent(i, f"Agent_{i}_{name}", h_base_val, bias))
            
        for i in range(8):
            self.agents[i].neighbors = [(i - 1) % 8, (i + 1) % 8]
            
        self.referee = LatticeRootReferee(num_agents=8)
        self.step_count = 0
        self.is_running = False
        self.timer = None
        
        # 3-Pane Geometry Layout Setup
        self.fig, (self.ax_lattice, self.ax_mass, self.ax_metric) = plt.subplots(3, 1, figsize=(13, 11))
        plt.subplots_adjust(bottom=0.18, hspace=0.45, top=0.94)
        
        self._setup_plots()
        self._setup_controls()
        
    def _init_transcript_file(self):
        timestamp = datetime.utcnow().isoformat() + "Z"
        header = f"\n==================================================\n" \
                 f"FPT LATTICE v3.6 INITIALIZED: {timestamp}\n" \
                 f"Features: 3-Pane Telemetry Matrix & Real-Time Agent Mass Streams\n" \
                 f"Root Authority Anchor: 99733-Q\n" \
                 f"==================================================\n"
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(header)
        log.info(f"Persistent transcript engine streaming to: {self.transcript_path}")

    def _write_to_transcript(self, text: str):
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def _setup_plots(self):
        # Pane 1: Spatial Octagonal Map
        self.ax_lattice.set_title("8-Agent Structural Grid (Node Radii = Total Integrated Mass [W_state + h])")
        self.ax_lattice.set_xlim(-2.5, 2.5)
        self.ax_lattice.set_ylim(-2.5, 2.5)
        self.ax_lattice.set_aspect('equal')
        
        self.angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
        self.node_x = 1.8 * np.cos(self.angles)
        self.node_y = 1.8 * np.sin(self.angles)
        
        for i in range(8):
            next_i = (i + 1) % 8
            self.ax_lattice.plot([self.node_x[i], self.node_x[next_i]], [self.node_y[i], self.node_y[next_i]], 
                                 color='#bbbbbb', linestyle='-', linewidth=1.5, zorder=1)
            
        self.cross_lines = []
        for i in range(8):
            for j in range(i + 2, 8):
                if (j - i) != 7:
                    line, = self.ax_lattice.plot([self.node_x[i], self.node_x[j]], [self.node_y[i], self.node_y[j]], 
                                                 color='#e8d7ff', linestyle=':', alpha=0.4, linewidth=1.0, zorder=1)
                    self.cross_lines.append((i, j, line))
            
        self.node_scatter = self.ax_lattice.scatter(self.node_x, self.node_y, s=150, 
                                                    c=self.angles, cmap='coolwarm', edgecolors='black', zorder=3)
        
        for i, agent in enumerate(self.agents):
            self.ax_lattice.text(self.node_x[i]*1.25, self.node_y[i]*1.25, f"A_{i}", 
                                 fontsize=9, ha='center', va='center', weight='bold')

        # Pane 2: Individual Agent Mass Streaming Real-Time Chart
        self.ax_mass.set_title("Individual Agent Metabolic Mass Streams (Side-by-Side Runtime Drift)")
        self.ax_mass.set_ylabel("Mass Value (W_state + h)")
        self.mass_colors = plt.cm.get_cmap('tab10', 8)
        self.mass_lines = []
        for i, agent in enumerate(self.agents):
            line, = self.ax_mass.plot([], [], color=self.mass_colors(i), linewidth=1.5, label=f"A_{i}: {agent.name.split('_')[1]}")
            self.mass_lines.append(line)
        self.ax_mass.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8, borderaxespad=0.)

        # Pane 3: System-wide Resilience Variance Logs
        self.ax_metric.set_title("Lattice Boundary Variance History (Network Structural Resilience)")
        self.ax_metric.set_ylabel("Global Variance Signature")
        self.metric_line, = self.ax_metric.plot([], [], color='#00cc88', marker='x', markersize=4)

    def _setup_controls(self):
        ax_toggle = plt.axes([0.15, 0.04, 0.2, 0.04])
        self.btn_toggle = Button(ax_toggle, 'Start Ticker Engine')
        self.btn_toggle.on_clicked(self._toggle_engine)

        ax_slider = plt.axes([0.5, 0.04, 0.35, 0.04])
        self.slider_speed = Slider(ax_slider, 'Ticker (ms)', 100, 2000, valinit=self.interval_ms, valstep=50)
        self.slider_speed.on_changed(self._update_speed)

    def _update_speed(self, val):
        self.interval_ms = int(val)
        if self.is_running and self.timer is not None:
            self.timer.stop()
            self._run_ticker_step()

    def _toggle_engine(self, event):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.label.set_text('Halt Ticker Engine')
            log.info(f"Ticker engine online. Operational frequencies set to: {self.interval_ms} ms.")
            self._run_ticker_step()
        else:
            self.btn_toggle.label.set_text('Start Ticker Engine')
            if self.timer is not None:
                self.timer.stop()
            log.info("Ticker loop paused.")

    def _run_ticker_step(self):
        if not self.is_running:
            return
        self._network_pulse_cycle()
        self.timer = self.fig.canvas.new_timer(interval=self.interval_ms)
        self.timer.add_callback(self._run_ticker_step)
        self.timer.start()

    def _network_pulse_cycle(self):
        self.step_count += 1
        delta_tick = 1.0
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        cycle_header = f"\n⚡ --- COUPLING PULSE CYCLE #{self.step_count} [{timestamp}] ---"
        print(cycle_header)
        self._write_to_transcript(cycle_header)
        
        current_snapshots = [a.state.copy() for a in self.agents]
        
        agent_tensions = np.zeros(8)
        for i, j, _ in self.cross_lines:
            diff = float(np.linalg.norm(current_snapshots[i] - current_snapshots[j]))
            if diff > 1.2:
                agent_tensions[i] += diff
                agent_tensions[j] += diff

        for i, agent in enumerate(self.agents):
            agent.update_elastic_gears(agent_tensions[i])
            neighbor_vectors = [current_snapshots[n_idx] for n_idx in agent.neighbors]
            pooled_input = np.mean(neighbor_vectors, axis=0)
            
            agent.process_network_input(pooled_input, delta_tick)
            
            symbolic_line = agent.translate_to_symbols()
            print(symbolic_line)
            self._write_to_transcript(symbolic_line)
            
        variance, is_healthy = self.referee.evaluate_lattice(self.agents)
        metric_line = f"📊 SYSTEM METRIC | Network Boundary Variance Signature: {variance:.4f}"
        print(metric_line)
        self._write_to_transcript(metric_line)
        
        if not is_healthy:
            override_msg = f"⚠️  CRITICAL FLAT DEADLOCK! Authority {self.referee.authority} deploying variance vectors."
            print(override_msg)
            self._write_to_transcript(override_msg)
            for agent in self.agents:
                agent.state += np.array([0.317, 0.104, 0.099]) * (agent.id + 1)
                agent.calculate_total_mass()
                
        self._update_plots()

    def _update_plots(self):
        # 1. Update Spatial Nodes
        sizes = [max(50, a.mass * 60) for a in self.agents]
        self.node_scatter.set_sizes(sizes)
        
        # 2. Update Cross Links
        for i, j, line in self.cross_lines:
            diff = np.linalg.norm(self.agents[i].state - self.agents[j].state)
            if diff > 1.2:
                line.set_color('#ff00ff')
                line.set_linewidth(1.4)
                line.set_alpha(0.8)
                line.set_linestyle('-')
            else:
                line.set_color('#e8d7ff')
                line.set_linewidth(1.0)
                line.set_alpha(0.2)
                line.set_linestyle(':')
        
        # 3. Update Individual Agent Mass Streams Side-by-Side Pane
        for i, agent in enumerate(self.agents):
            x_data = range(len(agent.mass_history))
            self.mass_lines[i].set_data(x_data, agent.mass_history)
        self.ax_mass.relim()
        self.ax_mass.autoscale_view()

        # 4. Update Global Resilience Variance Plot
        self.metric_line.set_data(range(len(self.referee.global_shadow_history)), self.referee.global_shadow_history)
        self.ax_metric.relim()
        self.ax_metric.autoscale_view()
        
        self.fig.canvas.draw_idle()

    def run(self):
        print("Sandbox activated. 3-Pane Telemetry environment monitoring individual agent mass is online.")
        plt.show()

if __name__ == "__main__":
    sandbox = FPTLatticeSandbox()
    sandbox.run()
