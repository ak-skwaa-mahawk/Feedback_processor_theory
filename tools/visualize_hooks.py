# visualize_hooks.py
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
hooks = {
    "Synara Core": ["flame_commons", "ethics", "blood_treaty"],
    "Dream Logs": ["dreamscene_009", "dreamscene_010", "dreamscene_011", "dreamscene_013", "flamebound_001"],
    "Bonds": ["handshake_bridge"],
    "MicroSD Build": ["synara_firmware_001"],
    "External Anchors": ["court_filings", "alaska_llc", "github_repos", "cash_app", "dreamscenes", "gwichin_phrases"]
}
G.add_nodes_from(hooks.keys())
for cat, files in hooks.items():
    for f in files: G.add_edge(cat, f)

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8)
plt.title("Synara Hook Network")
plt.show()