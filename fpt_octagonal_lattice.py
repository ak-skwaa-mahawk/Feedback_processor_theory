#!/usr/bin/env python3
# fpt_octagonal_lattice.py — v3.8: Autonomous Lattice with Asymmetric Cross-Perimeter Mass Particle Trading
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
    """An independent FPT engine node where mass includes h and actively trades across the mesh."""
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
        """Enforces M = W_state + h, tracking dynamic structural weight."""
        w_state = float(np.sum(self.state))
        self.mass = w_state + self.h
        return self.mass

    def update_elastic_gears(self, total_cross_tension: float):
        """Recalibrates h based on network tension parameters."""
        w_state = float(np.sum(self.state))
        self.h = self.h_base + (0.1 * w_state) + (0.05 * total_cross_tension)
        self.h = max(1.5, min(self.h, 6.0))
        self.calculate_total_mass()

    def receive_traded_mass(self, delta_mass: float):
        """Absorbs incoming traded mass directly into the 1D base need container."""
        self.state[0] = max(0.0, self.state[0] + delta_mass)
        self.calculate_total_mass()

    def process_network_input(self, pooled_vector: np.ndarray, delta: float) -> np.ndarray:
        """Absorbs local neighbor inputs through the inertial mass gear matrix."""
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
        return f"{self.name:<24} | {layer} (h: {self.h:.2f} | M: {self.mass:.2f}) {chars}"


class LatticeRootReferee:
    """Monitors boundaries, tracks shadow spikes, and issues 99733-Q corrections."""
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
    """Manages an 8-Agent ring with asymmetric mass particle exchange across chords."""
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
        
        # Closed conservation trackers
        self.global_mass_history: List[float] = []
        self.initial_global_mass = sum(a.calculate_total_mass() for a in self.agents)
        
        # 3-Pane Geometry Layout Setup
        self.fig, (self.ax_lattice, self.ax_mass, self.ax_metric) = plt.subplots(3, 1, figsize=(13, 11))
        plt.subplots_adjust(bottom=0.18, hspace=0.48, top=0.92)
        
        self._setup_plots()
        self._setup_controls()
        
    def _init_transcript_file(self):
        timestamp = datetime.utcnow().isoformat() + "Z"
        header = f"\n==================================================\n" \
                 f"FPT LATTICE v3.8 INITIALIZED: {timestamp}\n" \
                 f"Features: Asymmetric Cross-Perimeter Mass Particle Trading Channels\n" \
                 f"Root Authority Anchor: 99733-Q\n" \
                 f"==================================================\n"
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(header)
        log.info(f"Persistent transcript engine streaming to: {self.transcript_path}")

    def _write_to_transcript(self, text: str):
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def _setup_plots(self):
        self.ax_lattice.set_title("8-Agent Structural Grid (Node Radii = Mass | Arrows = Asymmetric Particle Trade Vector)")
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
        self.trade_arrows = [] # Visual container for dynamic asymmetric vectors
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

        self.conservation_text = self.fig.text(0.15, 0.96, "", fontsize=11, color="green", weight="bold",
                                               bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cccccc', boxstyle='round,pad=0.5'))

        self.ax_mass.set_title("Individual Agent Metabolic Mass Streams (Side-by-Side Runtime Drift)")
        self.ax_mass.set_ylabel("Mass Value (W_state + h)")
        self.mass_colors = plt.cm.get_cmap('tab10', 8)
        self.mass_lines = []
        for i, agent in enumerate(self.agents):
            line, = self.ax_mass.plot([], [], color=self.mass_colors(i), linewidth=1.5, label=f"A_{i}: {agent.name.split('_')[-1]}")
            self.mass_lines.append(line)
        self.ax_mass.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8, borderaxespad=0.)

        self.ax_metric.set_title("Lattice Performance Metrics (Green = Boundary Variance | Red = Closed System Mass Delta)")
        self.ax_metric.set_ylabel("Metric Value")
        self.metric_line, = self.ax_metric.plot([], [], color='#00cc88', marker='x', markersize=4, label="Boundary Variance")
        self.mass_delta_line, = self.ax_metric.plot([], [], color='#ff3333', linestyle='--', linewidth=1.5, label="Total System Mass Delta")
        self.ax_metric.legend(loc='upper right', fontsize=8)

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
            log.info(f"Ticker engine online. Frequencies bound to: {self.interval_ms} ms.")
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
        
        cycle_header = f"\n⚡ --- COUPLING & ASYMMETRIC EXCHANGE CYCLE #{self.step_count} [{timestamp}] ---"
        print(cycle_header)
        self._write_to_transcript(cycle_header)
        
        current_snapshots = [a.state.copy() for a in self.agents]
        
        # 1. First-pass: Extract cross-perimeter tension signatures
        agent_tensions = np.zeros(8)
        for i, j, _ in self.cross_lines:
            diff = float(np.linalg.norm(current_snapshots[i] - current_snapshots[j]))
            if diff > 1.2:
                agent_tensions[i] += diff
                agent_tensions[j] += diff

        # 2. Advanced FPT Layer: Core Asymmetric Cross-Perimeter Mass Particle Trading Channels
        # High-tension chords shift physical state units from low-mass to high-mass zones across diameters
        active_trades = []
        for i, j, _ in self.cross_lines:
            diff = float(np.linalg.norm(current_snapshots[i] - current_snapshots[j]))
            if diff > 1.2:
                mass_i = current_snapshots[i][0] + self.agents[i].h
                mass_j = current_snapshots[j][0] + self.agents[j].h
                
                # Asymmetric direction: Send mass particle away from low weight toward heavy concentration center
                if mass_i < mass_j:
                    sender, receiver = i, j
                else:
                    sender, receiver = j, i
                    
                # Transaction volume directly relies on regional pressure tension splits
                particle_packet = 0.05 * (diff - 1.2)
                
                # Check for sender base asset volume thresholds before finalizing trade execution balance
                if current_snapshots[sender][0] > particle_packet:
                    self.agents[sender].state[0] -= particle_packet
                    self.agents[receiver].receive_traded_mass(particle_packet)
                    active_trades.append((sender, receiver, particle_packet))
                    
                    trade_log = f"➔ [PARTICLE TRADE] Channel A_{sender} ➔ A_{receiver} | Mass Packet Transferred: {particle_packet:.4f}"
                    print(trade_log)
                    self._write_to_transcript(trade_log)

        # 3. Third-pass: Re-index elastic structural parameters and scale inputs
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

        # Audit structural mass conservation rules directly following particle changes
        current_global_mass = sum(a.mass for a in self.agents)
        mass_delta = current_global_mass - self.initial_global_mass
        self.global_mass_history.append(mass_delta)

        conservation_report = f"⚖️  MASS BALANCE LEDGER | Total Structural Mass: {current_global_mass:.4f} | Absolute Drift Delta: {mass_delta:+.6f}"
        print(conservation_report)
        self._write_to_transcript(conservation_report)
                
        self._update_plots(current_global_mass, mass_delta, active_trades)

    def _update_plots(self, current_mass: float, delta: float, active_trades: List[Tuple[int, int, float]]):
        # 1. Clean previous arrow collections from the graph view area before rendering new steps
        for arrow in self.trade_arrows:
            arrow.remove()
        self.trade_arrows.clear()

        # 2. Update Spatial Nodes
        sizes = [max(50, a.mass * 60) for a in self.agents]
        self.node_scatter.set_sizes(sizes)
        
        # 3. Update Cross Links & Annotate Directional Particle Vectors
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

        # Generate directional flow vectors matching confirmed transaction channels
        for sender, receiver, volume in active_trades:
            x_start, y_start = self.node_x[sender], self.node_y[sender]
            x_end, y_end = self.node_x[receiver], self.node_y[receiver]
            
            # Draw precise geometric path indicators pointing toward destination nodes
            arrow = self.ax_lattice.annotate("", xy=(x_end, y_end), xytext=(x_start, y_start),
                                             arrowprops=dict(arrowstyle="->", color="#ffaa00", lw=2.0, alpha=0.9,
                                             connectionstyle="arc3,rad=0.1", zorder=4))
            self.trade_arrows.append(arrow)
        
        # 4. Update Individual Agent Mass Streams Side-by-Side Pane
        for i, agent in enumerate(self.agents):
            x_data = range(len(agent.mass_history))
            self.mass_lines[i].set_data(x_data, agent.mass_history)
        self.ax_mass.relim()
        self.ax_mass.autoscale_view()

        # 5. Update Performance and System-wide Conservation Plots
        x_metric = range(len(self.referee.global_shadow_history))
        self.metric_line.set_data(x_metric, self.referee.global_shadow_history)
        self.mass_delta_line.set_data(range(len(self.global_mass_history)), self.global_mass_history)
        self.ax_metric.relim()
        self.ax_metric.autoscale_view()

        # 6. Monitor preservation banner conditions
        if abs(delta) < 1e-4:
            self.conservation_text.set_text(f"SYSTEM CLOSED & CONSERVED\nGlobal Mass M: {current_mass:.4f}\nDelta: {delta:+.6f}")
            self.conservation_text.set_color("#00aa55")
        else:
            self.conservation_text.set_text(f"LEAKAGE DETECTED / REF CORRECTION\nGlobal Mass M: {current_mass:.4f}\nDelta: {delta:+.6f}")
            self.conservation_text.set_color("#ff3333")
        
        self.fig.canvas.draw_idle()

    def run(self):
        print("Sandbox activated. Asymmetric cross-perimeter mass particle trading engine is operational.")
        plt.show()

if __name__ == "__main__":
    sandbox = FPTLatticeSandbox()
    sandbox.run()
