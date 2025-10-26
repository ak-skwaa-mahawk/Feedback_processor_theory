# tools/visualize_coherence.py
import networkx as nx
import matplotlib.pyplot as plt
from core.multi_agent_flame import MultiAgentFlameNetwork

network = MultiAgentFlameNetwork(5, "ring")
network.propagate_flame()

G = nx.cycle_graph(5)
pos = nx.circular_layout(G)
labels = {i: f"T={a.state[0]:.2f}, I={a.state[1]:.2f}, F={a.state[2]:.2f}" for i, a in enumerate(network.agents)}

nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', font_size=8)
plt.title("Real-Time Flame Network Coherence")
plt.savefig("flame_coherence.png")
plt.show()