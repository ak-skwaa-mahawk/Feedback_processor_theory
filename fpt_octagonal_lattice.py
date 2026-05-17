#!/usr/bin/env python3
# fpt_octagonal_lattice.py — v3.3: Autonomous Ticker Network with Speed Control & Cross-Perimeter Geometry Links
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
    """An independent FPT engine node within an 8-agent octagonal structural network."""
    def __init__(self, agent_id: int, name: str, h_factor: float, stance_offset: float):
        self.id = agent_id
        self.name = name
        self.h = h_factor
        self.stance_offset = stance_offset
        self.state = np.array([1.0, 0.1 * agent_id, 0.0], dtype=float)
        self.neighbors: List[int] = [] 

    def process_network_input(self, pooled_vector: np.ndarray, delta: float) -> np.ndarray:
        """Absorbs the collective neighbor push and generates an asymmetric counter-response."""
        mixed_base = (self.state * 0.3) + (pooled_vector * 0.7)
        
        take = 2.0 * (1.0 / (self.h + self.stance_offset))
        leave = 1.0 / (self.h - self.stance_offset)
        
        step_mod = np.array([-take, take - leave, leave], dtype=float)
        updated_state = np.maximum(mixed_base + step_mod * delta, 0.0)
        
        total = np.sum(updated_state)
        if total > 0:
            updated_state = (updated_state / total) * (np.sum(self.state) + delta)
            
        self.state = updated_state.copy()
        return self.state

    def translate_to_symbols(self) -> str:
        """Translates continuous vector weights into discrete symbolic strings based on dimensional density."""
        w1, w2, w3 = self.state[0], self.state[1], self.state[2]
        
        if w1 > w2 and w1 > w3:
            layer = "✦ [1D NEED: SEED]"
            chars = "⚬ ── ➔"
        elif w2 > w1 and w2 > w3:
            layer = "❖ [2D MESH: PLANE]"
            chars = "☩ ── ◈"
        else:
            layer = "▲ [3D VOL: ARCH]"
            chars = "⎔ ── ❖"
            
        return f"{self.name:<24} | {layer} (Weights: {w1:.2f}, {w2:.2f}, {w3:.2f}) {chars}"


class LatticeRootReferee:
    """Monitors octagonal boundary connectivity, shadow debt spikes, and issues 99733-Q overrides."""
    def __init__(self, num_agents: int):
        self.authority = "99733-Q"
        self.num_agents = num_agents
        self.global_shadow_history: List[float] = []

    def evaluate_lattice(self, agents: List[OctoLatticeAgent]) -> Tuple[float, bool]:
        """Evaluates total variance across the octagonal perimeter to check for flat-loop gridlocks."""
        all_states = np.array([a.state for a in agents])
        centroid = np.mean(all_states, axis=0)
        
        lattice_variance = float(np.sum([np.linalg.norm(a.state - centroid) for a in agents]))
        self.global_shadow_history.append(lattice_variance)
        
        is_dynamic = lattice_variance > 1.5
        return lattice_variance, is_dynamic


class FPTLatticeSandbox:
    """Manages an 8-Agent network structured as an octagonal ring with real-time ticker adjustments and cross-perimeter links."""
    def __init__(self, transcript_file: str = "fpt_lattice_transcript.txt"):
        self.transcript_path = Path(transcript_file)
        self._init_transcript_file()
        
        self.interval_ms = 1000  # Default to 1 second
        
        names = [
            "Einstein_Core", "Planar_Observer", "Base_Need_Anchor", "Mesh_Validator",
            "Volume_Builder", "Extractive_Mirror", "Generative_Sovereign", "Boundary_Lock"
        ]
        
        self.agents: List[OctoLatticeAgent] = []
        for i, name in enumerate(names):
            h_val = 3.1415 + (i * 0.05) - 0.15
            bias = 0.03 if i % 2 == 0 else -0.03
            self.agents.append(OctoLatticeAgent(i, f"Agent_{i}_{name}", h_val, bias))
            
        for i in range(8):
            self.agents[i].neighbors = [(i - 1) % 8, (i + 1) % 8]
            
        self.referee = LatticeRootReferee(num_agents=8)
        self.step_count = 0
        self.is_running = False
        self.timer = None
        
        # Canvas Geometry Windows Setup
        self.fig = plt.figure(figsize=(13, 9))
        self.ax_lattice = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        self.ax_metric = plt.subplot2grid((3, 1), (2, 0))
        plt.subplots_adjust(bottom=0.22, hspace=0.4)
        
        self._setup_plots()
        self._setup_controls()
        
    def _init_transcript_file(self):
        """Initializes or appends to a persistent rolling file ledger with clear session headers."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        header = f"\n==================================================\n" \
                 f"FPT LATTICE v3.3 LOADED: {timestamp}\n" \
                 f"Features: Speed Ticker Controls & Cross-Perimeter Mesh Mapping\n" \
                 f"Root Authority Anchor: 99733-Q\n" \
                 f"==================================================\n"
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(header)
        log.info(f"Persistent transcript engine streaming to: {self.transcript_path}")

    def _write_to_transcript(self, text: str):
        """Appends a single structured entry to the rolling file log."""
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def _setup_plots(self):
        self.ax_lattice.set_title("8-Agent Octagonal Lattice (Node Radii = 3D Vol | Lines = Structural Links & Cross-Perimeter Vectors)")
        self.ax_lattice.set_xlim(-2.5, 2.5)
        self.ax_lattice.set_ylim(-2.5, 2.5)
        self.ax_lattice.set_aspect('equal')
        
        self.angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
        self.node_x = 1.8 * np.cos(self.angles)
        self.node_y = 1.8 * np.sin(self.angles)
        
        # 1. Permanent perimeter loop ring setup
        for i in range(8):
            next_i = (i + 1) % 8
            self.ax_lattice.plot([self.node_x[i], self.node_x[next_i]], [self.node_y[i], self.node_y[next_i]], 
                                 color='#bbbbbb', linestyle='-', linewidth=1.5, zorder=1)
            
        # 2. Cross-Perimeter Structural Link Mapping (Opposite and transverse tension chords)
        self.cross_lines = []
        for i in range(8):
            for j in range(i + 2, 8):
                # Exclude immediate neighbors to focus pure visibility on inner axis paths
                if (j - i) != 7:
                    line, = self.ax_lattice.plot([self.node_x[i], self.node_x[j]], [self.node_y[i], self.node_y[j]], 
                                                 color='#e8d7ff', linestyle=':', alpha=0.4, linewidth=1.0, zorder=1)
                    self.cross_lines.append((i, j, line))
            
        self.node_scatter = self.ax_lattice.scatter(self.node_x, self.node_y, s=[200]*8, 
                                                    c=self.angles, cmap='coolwarm', edgecolors='black', zorder=3)
        
        self.text_labels = []
        for i, agent in enumerate(self.agents):
            lbl = self.ax_lattice.text(self.node_x[i]*1.25, self.node_y[i]*1.25, f"A_{i}", 
                                       fontsize=9, ha='center', va='center', weight='bold')
            self.text_labels.append(lbl)

        self.ax_metric.set_title("Lattice Boundary Variance History (Network Structural Resilience)")
        self.ax_metric.set_ylabel("Global Variance Signature")
        self.metric_line, = self.ax_metric.plot([], [], color='#00cc88', marker='x', markersize=4)

    def _setup_controls(self):
        # Action button position placement
        ax_toggle = plt.axes([0.15, 0.05, 0.2, 0.04])
        self.btn_toggle = Button(ax_toggle, 'Start Ticker Engine')
        self.btn_toggle.on_clicked(self._toggle_engine)

        # Interactive speed slider adjustment console line
        ax_slider = plt.axes([0.5, 0.05, 0.35, 0.04])
        self.slider_speed = Slider(ax_slider, 'Ticker (ms)', 100, 2000, valinit=self.interval_ms, valstep=50)
        self.slider_speed.on_changed(self._update_speed)

    def _update_speed(self, val):
        """Live updates ticker calculation thresholds directly from the slider console line."""
        self.interval_ms = int(val)
        if self.is_running and self.timer is not None:
            # Terminate and re-lock background canvas loops to apply updated speed frames immediately
            self.timer.stop()
            self._run_ticker_step()

    def _toggle_engine(self, event):
        """Switches background automated loops on and off dynamically."""
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.label.set_text('Halt Ticker Engine')
            log.info(f"Ticker loop engaged. Processing update steps every {self.interval_ms} ms.")
            self._run_ticker_step()
        else:
            self.btn_toggle.label.set_text('Start Ticker Engine')
            if self.timer is not None:
                self.timer.stop()
            log.info("Ticker loop paused.")

    def _run_ticker_step(self):
        """Autonomous frame generator loop."""
        if not self.is_running:
            return
        
        self._network_pulse_cycle()
        
        # Requests automated system updates using live speed variable counts
        self.timer = self.fig.canvas.new_timer(interval=self.interval_ms)
        self.timer.add_callback(self._run_ticker_step)
        self.timer.start()

    def _network_pulse_cycle(self):
        self.step_count += 1
        delta_tick = 1.0
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        cycle_header = f"\n⚡ --- PULSE CYCLE #{self.step_count} [{timestamp}] (Interval: {self.interval_ms}ms) ---"
        print(cycle_header)
        self._write_to_transcript(cycle_header)
        
        current_snapshots = [a.state.copy() for a in self.agents]
        
        for i, agent in enumerate(self.agents):
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
                
        self._update_plots()

    def _update_plots(self):
        # 1. Update primary node sizing metrics
        sizes = [max(50, np.sum(a.state) * 75) for a in self.agents]
        self.node_scatter.set_sizes(sizes)
        
        # 2. Dynamic Cross-Perimeter Geometric Vector Vectorization Realignment
        # Colors link pathways based on the absolute interaction difference between non-neighbor stations
        for i, j, line in self.cross_lines:
            diff = np.linalg.norm(self.agents[i].state - self.agents[j].state)
            # High interaction differences brighten chord states to indicate cross-boundary tension structures
            if diff > 1.2:
                line.set_color('#ff00ff')
                line.set_linewidth(1.2)
                line.set_alpha(0.7)
                line.set_linestyle('-')
            else:
                line.set_color('#e8d7ff')
                line.set_linewidth(1.0)
                line.set_alpha(0.3)
                line.set_linestyle(':')
        
        # 3. Process rolling logs updates
        self.metric_line.set_data(range(len(self.referee.global_shadow_history)), self.referee.global_shadow_history)
        self.ax_metric.relim()
        self.ax_metric.autoscale_view()
        
        self.fig.canvas.draw_idle()

    def run(self):
        print("Sandbox activated. Use the interactive slider console line to adjust runtime frequencies.")
        plt.show()

if __name__ == "__main__":
    sandbox = FPTLatticeSandbox()
    sandbox.run()
