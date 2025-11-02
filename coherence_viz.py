# coherence_viz.py
import torch
def viz_coherence(mesh):
    R_map = torch.tensor([calc_resonance(agent) for agent in mesh])
    heatmap = torch.softmax(R_map, dim=0)  # Flame intensity
    # Render: OpenGL swarm + entropy waves