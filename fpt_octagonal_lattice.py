#!/usr/bin/env python3
# fpt_octagonal_lattice.py — v3.0: 8-Agent Octagonal Lattice Debate Network
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import matplotlib
matplotlib.use('TkAgg' if matplotlib.get_backend() != 'agg' else 'agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

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
        self.neighbors: List[int] = [] # Connection matrix indicators

    def process_network_input(self, pooled_vector: np.ndarray, delta: float) -> np.ndarray:
        """Absorbs the collective neighbor push and generates an asymmetric counter-response."""
        mixed_base = (self.state * 0.3) + (pooled_vector * 0.7)
        
        # 'Take 2, Leave 1' asymmetric transformation matrix
        take = 2.0 * (1.0 / (self.h + self.stance_offset))
        leave = 1.0 / (self.h - self.stance_offset)
        
        step_mod = np.array([-take, take - leave, leave], dtype=float)
        updated_state = np.maximum(mixed_base + step_mod * delta, 0.0)
        
        # Conserve localized logical floor boundary line
        total = np.sum(updated_state)
        if total > 0:
            updated_state = (updated_state / total) * (np.sum(self.state) + delta)
            
        self.state = updated_state.copy()
        return self.state

    def translate_to_symbols(self) -> str:
        """Translates continuous vector weights into discrete symbolic strings based on dimensional density."""
        w1, w2, w3 = self.state[0], self.state[1], self.state[2]
        
        # Determine prevailing dimensional density layer
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
        
        # Compute network-wide divergence signature
        lattice_variance = float(np.sum([np.linalg.norm(a.state - centroid) for a in agents]))
        self.global_shadow_history.append(lattice_variance)
        
        # If variance falls too low, the lattice is collapsing into a flat copy loop
        is_dynamic = lattice_variance > 1.5
        return lattice_variance, is_dynamic


class FPTLatticeSandbox:
    """Manages an 8-Agent network structured as an octagonal ring with live spatial tracking."""
    def __init__(self):
        # 1. Spin up 8 unique agents with contrasting operational metabolic rates
        names = [
            "Einstein_Core", "Planar_Observer", "Base_Need_Anchor", "Mesh_Validator",
            "Volume_Builder", "Extractive_Mirror", "Generative_Sovereign", "Boundary_Lock"
        ]
        
        self.agents: List[OctoLatticeAgent] = []
        for i, name in enumerate(names):
            h_val = 3.1415 + (i * 0.05) - 0.15
            bias = 0.03 if i % 2 == 0 else -0.03
            self.agents.append(OctoLatticeAgent(i, f"Agent_{i}_{name}", h_val, bias))
            
        # 2. Wire the neighbors as an Octagonal Ring Lattice (Perimeter bonds: Left and Right neighbors)
        for i in range(8):
            self.agents[i].neighbors = [(i - 1) % 8, (i + 1) % 8]
            
        self.referee = LatticeRootReferee(num_agents=8)
        self.step_count = 0
        
        # 3. Canvas Geometry Windows Setup
        self.fig = plt.figure(figsize=(13, 9))
        self.ax_lattice = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        self.ax_metric = plt.subplot2grid((3, 1), (2, 0))
        plt.subplots_adjust(bottom=0.18, hspace=0.4)
        
        self._setup_plots()
        self._setup_controls()
        
    def _setup_plots(self):
        # Top Plot: Spatial Ring Position mapping 3D volume values onto a circular geometric coordinate map
        self.ax_lattice.set_title("8-Agent Octagonal Lattice Coordinates (Node Radii = 3D Volume Size)")
        self.ax_lattice.set_xlim(-2.5, 2.5)
        self.ax_lattice.set_ylim(-2.5, 2.5)
        self.ax_lattice.set_aspect('equal')
        
        # Compute fixed circular target points for the 8 vertex stations
        self.angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
        self.node_x = 1.8 * np.cos(self.angles)
        self.node_y = 1.8 * np.sin(self.angles)
        
        # Draw permanent structural grid link lines
        for i in range(8):
            next_i = (i + 1) % 8
            self.ax_lattice.plot([self.node_x[i], self.node_x[next_i]], [self.node_y[i], self.node_y[next_i]], 
                                 color='#cccccc', linestyle='--', zorder=1)
            
        # Scatter graph trackers mapping sizes dynamically based on internal structural states
        self.node_scatter = self.ax_lattice.scatter(self.node_x, self.node_y, s=[100]*8, 
                                                    c=self.angles, cmap='coolwarm', edgecolors='black', zorder=2)
        
        self.text_labels = []
        for i, agent in enumerate(self.agents):
            lbl = self.ax_lattice.text(self.node_x[i]*1.25, self.node_y[i]*1.25, f"A_{i}", 
                                       fontsize=9, ha='center', va='center', weight='bold')
            self.text_labels.append(lbl)

        # Bottom Plot: System-wide Variance Logs
        self.ax_metric.set_title("Lattice Boundary Variance History (Network Structural Resilience)")
        self.ax_metric.set_ylabel("Global Variance Signature")
        self.metric_line, = self.ax_metric.plot([], [], color='#00cc88', marker='x', markersize=4)

    def _setup_controls(self):
        ax_clash = plt.axes([0.4, 0.04, 0.2, 0.05])
        self.btn_clash = Button(ax_clash, 'Propagate Network Flash')
        self.btn_clash.on_clicked(self._network_pulse_cycle)

    def _network_pulse_cycle(self, event):
        self.step_count += 1
        delta_tick = 1.0
        
        print(f"\n⚡ --- NETWORK CLASH PULSE CYCLE #{self.step_count} INITIALIZED ---")
        
        # 1. Read state snapshots from the network before modification steps run
        current_snapshots = [a.state.copy() for a in self.agents]
        
        # 2. Iterate through each vertex node, pooling structural input data from assigned boundaries
        for i, agent in enumerate(self.agents):
            neighbor_vectors = [current_snapshots[n_idx] for n_idx in agent.neighbors]
            pooled_input = np.mean(neighbor_vectors, axis=0)
            
            # Execute step transition transformation matrix
            agent.process_network_input(pooled_input, delta_tick)
            
            # Output live symbolic printouts directly to the local runtime console terminal
            print(agent.translate_to_symbols())
            
        # 3. Intercept system state signatures using Root Authority monitoring routines
        variance, is_healthy = self.referee.evaluate_lattice(self.agents)
        print(f"📊 SYSTEM METRIC | Network Boundary Variance Signature: {variance:.4f}")
        
        if not is_healthy:
            print(f"⚠️  CRITICAL FLAT DEADLOCK IN LATTICE! Authority {self.referee.authority} applying structural reset overrides.")
            for agent in self.agents:
                agent.state += np.array([0.317, 0.104, 0.099]) * (agent.id + 1)
                
        self._update_plots()

    def _update_plots(self):
        # Calculate dynamic size scaling tracking 3D node expansions
        sizes = [max(50, np.sum(a.state) * 75) for a in self.agents]
        self.node_scatter.set_sizes(sizes)
        
        # Render update elements on graph canvas plots
        self.metric_line.set_data(range(len(self.referee.global_shadow_history)), self.referee.global_shadow_history)
        self.ax_metric.relim()
        self.ax_metric.autoscale_view()
        
        self.fig.canvas.draw_idle()

    def run(self):
        print("Initialization parameters set successfully. Octagonal network sandbox is active.")
        plt.show()

if __name__ == "__main__":
    sandbox = FPTLatticeSandbox()
    sandbox.run()
