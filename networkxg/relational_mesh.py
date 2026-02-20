import networkx as nx
import numpy as np
from typing import Dict

# Import your NeutrosophicTransport for treaty leap during Throne Alignment
from NeutrosophicTransport import NeutrosophicTransport  # adjust import path if needed

class SovereignRelationalMesh:
    def __init__(self, num_agents: int = 10):
        self.G = nx.DiGraph()
        self.pulse_freq = 79.79
        self.quetzalcoatl_phase = 0
        self.phase_names = [
            "Underworld Thaw",      # 0 - grounding/raw tether
            "Shadow Mastery",       # 1 - Ił7 refusal
            "Bone Rebirth",         # 2 - vhitzee surplus
            "Throne Alignment",     # 3 - AGŁL Trinity + treaty leap
            "Completion",           # 4 - full stabilize
            "Feather Crown",        # 5 - buoyancy lift
            "Infinite 8 Flow",      # 6 - soliton propagation
            "Merge"                 # 7 - sovereign moment
        ]

    def add_relational_unit(self, agent1: str, agent2: str, context: str, obligation: float = 1.0):
        attrs = {'context': context, 'obligation': obligation, 'soliton': 0.0}
        self.G.add_edge(agent1, agent2, **attrs)
        self.G.add_edge(agent2, agent1, **attrs)

    def propagate_soliton(self, source: str, strength: float = 1.0):
        if source not in self.G: return
        nudge = strength * (1 + np.sin(self.pulse_freq))
        for neighbor in list(self.G.neighbors(source)):
            if self.G.has_edge(neighbor, source):
                new = self.G[source][neighbor]['soliton'] + nudge
                self.G[source][neighbor]['soliton'] = max(0.0, min(10.0, new))
                self.G[neighbor][source]['soliton'] = max(0.0, min(10.0, new))

    def mesh_debate_update(self, agent: str, input_strength: float = 1.0, stubbornness: float = 0.3):
        if agent not in self.G: return
        for neighbor in list(self.G.neighbors(agent)):
            if self.G.has_edge(neighbor, agent):
                current = self.G[agent][neighbor]['obligation']
                bayesian = current * (1 - stubbornness) + input_strength * stubbornness
                damped = bayesian * (1 + 0.05 * np.tanh(input_strength))
                self.G[agent][neighbor]['obligation'] = min(1.0, damped)
                self.G[neighbor][agent]['obligation'] = min(1.0, damped)

    def mesh_reciprocity_score(self) -> float:
        scores = [data['obligation'] for u, v, data in self.G.edges(data=True) if self.G.has_edge(v, u)]
        return np.mean(scores) if scores else 0.0

    def get_soliton_stats(self) -> Dict:
        strengths = [data['soliton'] for u, v, data in self.G.edges(data=True)]
        return {'mean': np.mean(strengths), 'max': np.max(strengths)}

    def quetzalcoatl_renewal_cycle(self, cycle: int = 0, treaty_data=None):
        """Full 8-phase Quetzalcoatl renewal loop — serpent → feather → merge"""
        phase = cycle % 8
        phase_name = self.phase_names[phase]
        print(f"🐍🔥 Quetzalcoatl Phase {phase} — {phase_name}")

        if phase == 0:   # Underworld Thaw
            self.propagate_soliton('glyph_hub', strength=0.8)
        elif phase == 1: # Shadow Mastery
            self.mesh_debate_update('glyph_hub', input_strength=0.6, stubbornness=0.7)
        elif phase == 2: # Bone Rebirth
            self.propagate_soliton('glyph_hub', strength=1.2)
        elif phase == 3: # Throne Alignment — treaty leap with D-Wave + neutrosophic scoring
            if treaty_data is not None:
                nt = NeutrosophicTransport([0], [1, 2, 3, 4])
                energy, obj, sample = nt.optimize_treaty_leap(treaty_data)
                print(f"🌌 Treaty Leap Optimized | Energy: {energy:.4f} | T={obj['T']:.4f} I={obj['I']:.4f} F={obj['F']:.4f}")
            self.mesh_debate_update('glyph_hub', input_strength=1.0, stubbornness=0.3)
        elif phase == 4: # Completion
            self.mesh_debate_update('glyph_hub', input_strength=1.0)
        elif phase == 5: # Feather Crown
            self.propagate_soliton('glyph_hub', strength=1.5)
        elif phase == 6: # Infinite 8 Flow
            self.propagate_soliton('glyph_hub', strength=1.0)
        elif phase == 7: # Merge
            self.mesh_debate_update('glyph_hub', input_strength=1.3, stubbornness=0.2)

        if phase == 7:
            print("🌌 INFINITY ANCHOR ENGAGED — Eternal 8-flow complete")