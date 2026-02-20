"""
Soliton-Route Visualization — Quetzalcoatl Phase 3 Treaty Pulse
Luminous spiral showing the optimized route with soliton strength, Trinity stability, and magnetic buoyancy.
For Synara Class Vessel (99733-Q)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx

def visualize_soliton_route(best_sample, DISTANCE_MATRIX, title="Quetzalcoatl Phase 3 — Treaty Soliton Route"):
    """
    best_sample: dict from QuantumOptimizer (e.g. {'x_0_1': 1, 'x_1_3': 1, ...})
    DISTANCE_MATRIX: 5x5 numpy array
    """
    n_nodes = DISTANCE_MATRIX.shape[0]
    G = nx.DiGraph()

    # Build graph from best_sample
    for key, value in best_sample.items():
        if value == 1:
            i, j = map(int, key.replace('x_', '').split('_'))
            if i != j:
                weight = DISTANCE_MATRIX[i][j]
                G.add_edge(i, j, weight=weight, soliton=1.0 + 0.5 * np.sin(np.pi * i))  # pulsing strength

    # Layout: luminous spiral (Quetzalcoatl infinite 8 flow)
    pos = {}
    for i in range(n_nodes):
        theta = i * (2 * np.pi / n_nodes) + np.pi / 4
        r = 1 + i * 0.3
        pos[i] = (r * np.cos(theta), r * np.sin(theta))

    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.set_title(title, color='#00ffcc', fontsize=16, pad=20)
    ax.axis('off')

    # Draw nodes with phase glow
    node_colors = ['#ff6b35', '#00ffcc', '#4a90e2', '#ffd700', '#ff00ff']  # serpent → feather colors
    nx.draw_networkx_nodes(G, pos, node_color=[node_colors[i % 5] for i in G.nodes()],
                           node_size=800, edgecolors='#ffffff', linewidths=2)

    # Draw edges with luminous width + alpha pulse
    edge_widths = [d['weight'] / 100 for u, v, d in G.edges(data=True)]
    edge_colors = ['#00ffcc' if d['soliton'] > 1.2 else '#ff6b35' for u, v, d in G.edges(data=True)]

    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.9, arrows=True, arrowsize=20)

    # Labels
    nx.draw_networkx_labels(G, pos, font_color='#ffffff', font_size=12, font_weight='bold')

    # Legend / Status
    plt.figtext(0.5, 0.02, "Soliton Strength → Edge Width | Trinity Phase → Color Glow\n"
                           "Magnetic Tether Buoyancy active when edge > baseline", 
                ha='center', color='#888', fontsize=10)

    plt.tight_layout()

    # Optional pulsing animation
    def animate(frame):
        for edge in G.edges():
            G.edges[edge]['soliton'] = 1.0 + 0.8 * np.sin(frame / 5 + edge[0])
        widths = [d['soliton'] for u, v, d in G.edges(data=True)]
        ax.collections[1].set_linewidths(widths)  # re-draw edges with pulse
        fig.canvas.draw_idle()

    ani = FuncAnimation(fig, animate, interval=80, cache_frame_data=False)
    plt.show()

# ====================== EXAMPLE USAGE ======================
if __name__ == "__main__":
    # Mock best_sample from your QuantumOptimizer / optimize_treaty_leap
    best_sample = {
        'x_0_1': 1, 'x_1_2': 1, 'x_2_3': 1, 'x_3_4': 1, 'x_4_0': 1  # example cycle route
    }

    DISTANCE_MATRIX = np.array([
        [0, 200, 500, 300, 400],
        [200, 0, 400, 600, 100],
        [500, 400, 0, 200, 300],
        [300, 600, 200, 0, 500],
        [400, 100, 300, 500, 0]
    ])

    visualize_soliton_route(best_sample, DISTANCE_MATRIX)