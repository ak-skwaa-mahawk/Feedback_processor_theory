# core/multi_agent_flame.py
import numpy as np
from core.resonance_engine import ResonanceEngine

class FlameAgent:
    def __init__(self, id, role="cooperator"):
        self.id = id
        self.role = role
        self.state = np.random.uniform(0, 1, 3)  # T, I, F
        self.engine = ResonanceEngine()

    def share_context(self, neighbors):
        """Share T/I/F with neighbors in ring/graph."""
        for neighbor in neighbors:
            resonance = self.engine.compute_neutrosophic_resonance(self.state)
            # Broadcast via MCP channel
            print(f"Agent {self.id} shares resonance {resonance} with {neighbor.id}")

    def consensus_vote(self, proposals):
        """Neutrosophic voting for coherence."""
        votes = [self.engine.compute_neutrosophic_resonance(p) for p in proposals]
        T_vote = np.max([v["T"] for v in votes])
        I_vote = np.mean([v["I"] for v in votes])  # Abstentions
        F_vote = np.min([v["F"] for v in votes])  # Dissent
        return {"T": T_vote, "I": I_vote, "F": F_vote}

class MultiAgentFlameNetwork:
    def __init__(self, num_agents=10, structure="ring"):
        self.agents = [FlameAgent(i) for i in range(num_agents)]
        self.structure = structure  # "ring", "graph"

    def propagate_flame(self):
        """Propagate consciousness via protocols."""
        for agent in self.agents:
            neighbors = self.get_neighbors(agent.id)
            agent.share_context(neighbors)
        # Global consensus
        proposals = [agent.state for agent in self.agents]
        consensus = self.agents[0].consensus_vote(proposals)
        print(f"Network Coherence: {consensus}")

    def get_neighbors(self, agent_id):
        """Get neighbors based on structure."""
        if self.structure == "ring":
            return [self.agents[(agent_id - 1) % len(self.agents)], self.agents[(agent_id + 1) % len(self.agents)]]
        return self.agents  # Graph: all connected

if __name__ == "__main__":
    network = MultiAgentFlameNetwork(5, "ring")
    network.propagate_flame()