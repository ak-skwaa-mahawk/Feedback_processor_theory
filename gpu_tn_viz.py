# gpu_tn_viz.py
import cupy as cp
from flamegpu import *

def tn_flame_viz(model):
    # MPS contraction on GPU
    tensors = cp.random.randn(n_agents, 2, chi, chi)
    R = cp.tensordot(tensors, axes=([1,2],[0,1]))  # Fast
    # Viz: Coherence heatmap
    model.addVisualisation(R.get(), "flame_coherence")