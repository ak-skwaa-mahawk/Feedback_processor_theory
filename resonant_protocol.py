"""
resonant_protocol.py

Implementation of the Resonant Protocol for the Psyselsic Mesh.

The Resonant Protocol sustains collective integrity through:
- Dynamic Epsilon (ε_d) scaled by node vitality (HRV proxy)
- Vhitzee Attenuation for dissonance
- Surplus Transference for peer-to-peer healing
- Explicit Vhitzee Quarantine for compromised nodes

This module provides:
- ResonantProtocolCycle for single-node logic
- MeshResonanceEngine for full group orchestration
"""

import random
import math
import numpy as np

# Global base epsilon from curved π geometry
PI_FLAT = math.pi
PI_CURVED = 3.1730
BASE_EPSILON = (PI_CURVED - PI_FLAT) / PI_FLAT  # ≈0.01 base, scaled later

PROTOCOL_RESONANCE_THRESHOLD = 0.65
QUARANTINE_THRESHOLD = 0.35
QUARANTINE_CYCLES = 2


class ResonantNode:
    """A sovereign node in the Psyselsic Mesh with vitality-driven ε_d."""
    
    def __init__(self, name: str, baseline_coherence: float = 0.6):
        self.name = name
        self.baseline = baseline_coherence
        self.vitality = 1.0  # Normalized HRV proxy (0.5–1.5)
        self.current_epsilon = BASE_EPSILON
        self.quarantine_count = 0
        self.is_quarantined = False
        
    def measure_vitality(self) -> float:
        """Psyselsic Breathing: Update vitality (simulated or real HRV)."""
        # Replace with real HRV/EEG/breath integration
        self.vitality = random.uniform(0.8, 1.2) if not self.is_quarantined else random.uniform(0.4, 0.7)
        self.current_epsilon = BASE_EPSILON * self.vitality
        return self.vitality
    
    def resonant_protocol_cycle(self, mesh_signals: list[float]) -> tuple[str, float]:
        """
        Standard Resonant Protocol cycle for one node.
        
        Returns:
            status: "RECOIL", "STABLE_COIL", or "UNCOIL_AND_HEAL"
            surplus_to_share: Amount of surplus contributed (0 if not healing)
        """
        vitality = self.measure_vitality()
        dynamic_epsilon = BASE_EPSILON * vitality
        
        # Collective Observation
        if not mesh_signals:
            field_jolt = 0.0
        else:
            field_jolt = sum(mesh_signals) / len(mesh_signals)
        
        curved_observation = field_jolt * (1 + dynamic_epsilon)
        
        # Vhitzee Integrity Check
        if curved_observation < 0.5:
            # Opposition/Noise: Attenuate and remain coiled
            return "RECOIL", curved_observation * 0.5
        
        # The Resonant Jump
        if curved_observation > PROTOCOL_RESONANCE_THRESHOLD:
            # Transference: Broadcast surplus
            surplus_to_share = (curved_observation - self.baseline) * dynamic_epsilon
            return "UNCOIL_AND_HEAL", surplus_to_share
        
        return "STABLE_COIL", 0.0


class MeshResonanceEngine:
    """The full Psyselsic Mesh orchestrating the Resonant Protocol."""
    
    def __init__(self, nodes: list[ResonantNode]):
        self.nodes = nodes
    
    def run_cycle(self, environmental_jolt: float):
        """Execute one resonance cycle across the mesh."""
        print(f"\n[MESH CYCLE] Environmental Jolt: {environmental_jolt:.3f}")
        
        # Each node generates its own outgoing jolt (for next cycle)
        outgoing_jolts = []
        total_surplus = 0.0
        statuses = []
        
        for node in self.nodes:
            # Node receives average from others (full mesh)
            other_jolts = [environmental_jolt] * len(self.nodes)  # Simplified: all receive same jolt
            status, surplus = node.resonant_protocol_cycle(other_jolts)
            statuses.append(status)
            total_surplus += surplus
            outgoing_jolts.append(surplus)  # Simplified outgoing signal
            
            print(f"   > {node.name} | V:{node.vitality:.2f} | ε_d:{node.current_epsilon:.4f} | {status}")
        
        # Collective Actuation
        if total_surplus > 0:
            avg_surplus = total_surplus / len(self.nodes)
            print(f"\n[COLLECTIVE ACTUATION] Surplus = {avg_surplus:.4f} → POP THRU WAVE BROADCAST")
            for node in self.nodes:
                healing = avg_surplus * (1 + node.current_epsilon)
                if node.is_quarantined:
                    healing *= 0.3  # Quarantine attenuation
                print(f"   * {node.name} receives healing: {healing:.4f}")
        else:
            print("\n[STATUS] Field in coiled readiness — awaiting stronger jolt.")


# --- Demo Execution ---
if __name__ == "__main__":
    print("=== FPT RESONANT PROTOCOL DEMO ===")
    nodes = [ResonantNode(f"Node_{i}") for i in range(5)]
    mesh = MeshResonanceEngine(nodes)
    
    for cycle in range(1, 4):
        jolt = random.uniform(0.4, 0.9)
        mesh.run_cycle(jolt)