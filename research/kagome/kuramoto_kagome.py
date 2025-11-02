# research/kagome/kuramoto_kagome.py
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List

import numpy as np

try:
    import networkx as nx
except ImportError as e:
    raise SystemExit("Please `pip install networkx`") from e


def kagome_lattice(n_x: int, n_y: int, a: float = 1.0) -> Tuple[nx.Graph, np.ndarray]:
    """
    Build a finite kagome lattice (trihexagonal tiling) of size n_x by n_y unit cells.
    Returns:
      G: graph with nodes 0..N-1
      pos: (N,2) array of xy positions for plotting / geometry
    """
    # basis for kagome unit cell (3 sites)
    b = np.array([[0.0, 0.0],
                  [0.5, 0.0],
                  [0.25, math.sqrt(3)/4]], dtype=float) * a
    a1 = np.array([1.0, 0.0]) * a
    a2 = np.array([0.5, math.sqrt(3)/2]) * a

    coords: List[np.ndarray] = []
    for ix in range(n_x):
        for iy in range(n_y):
            R = ix * a1 + iy * a2
            for p in b:
                coords.append(R + p)

    pos = np.vstack(coords)
    N = pos.shape[0]
    G = nx.Graph()
    G.add_nodes_from(range(N))

    # connect near neighbors (within cutoff)
    cutoff = 0.6 * a  # approximate nn distance
    for i in range(N):
        for j in range(i + 1, N):
            d = np.linalg.norm(pos[i] - pos[j])
            if d < cutoff:
                G.add_edge(i, j, length=d)
    return G, pos


@dataclass
class KuramotoConfig:
    K: float = 1.0             # coupling strength
    dt: float = 0.01           # time step
    T: float = 10.0            # total time
    anisotropy: float = 0.0    # 0 = isotropic; >0 favors one lattice direction
    noise: float = 0.0         # phase noise amplitude
    seed: int = 907            # RNG seed
    rectangular_bias: float = 0.0  # “geometry” bias: 0 (none) .. 1 (strong)


def run_kuramoto_on_kagome(n_x: int = 6,
                           n_y: int = 6,
                           a: float = 1.0,
                           cfg: KuramotoConfig = KuramotoConfig()) -> Dict[str, Any]:
    """
    Simulate Kuramoto oscillators on a kagome graph. Returns synchronization metrics over time.
    Geometry knobs:
      - anisotropy: weights edges aligned with a1 vs a2 directions
      - rectangular_bias: scales couplings to emulate “rectangular vs parallelogram” pillars
    """
    rng = np.random.default_rng(cfg.seed)
    G, pos = kagome_lattice(n_x, n_y, a)
    N = G.number_of_nodes()

    # Natural frequencies: small spread around omega0
    omega0 = 2 * math.pi * 1.0  # 1 Hz (arbitrary units)
    omega = rng.normal(loc=omega0, scale=0.05 * omega0, size=N)

    # Initial phases
    theta = rng.uniform(0, 2 * math.pi, size=N)

    # Precompute edge weights with optional anisotropy & rectangular bias
    edge_i = []
    edge_j = []
    weights = []
    # Primitive directions for anisotropy test
    a1 = np.array([1.0, 0.0]) * a
    a2 = np.array([0.5, math.sqrt(3)/2]) * a

    def dir_weight(vec: np.ndarray) -> float:
        v = vec / (np.linalg.norm(vec) + 1e-12)
        w1 = abs(np.dot(v, a1) / (np.linalg.norm(a1) + 1e-12))
        w2 = abs(np.dot(v, a2) / (np.linalg.norm(a2) + 1e-12))
        w = 1.0 + cfg.anisotropy * (w1 - w2)
        return max(0.05, w)

    for i, j, data in G.edges(data=True):
        vec = pos[j] - pos[i]
        w = dir_weight(vec)
        # Pillar “rectangular vs parallelogram” proxy:
        # bias couplings based on y-position to emulate shape effects
        pillar = 1.0 - cfg.rectangular_bias * (abs(pos[i, 1]) + abs(pos[j, 1])) / (a * max(n_y, 1))
        edge_i.append(i)
        edge_j.append(j)
        weights.append(max(0.01, w * pillar))

    edge_i = np.array(edge_i, dtype=int)
    edge_j = np.array(edge_j, dtype=int)
    weights = np.array(weights, dtype=float)

    steps = int(cfg.T / cfg.dt)
    order_param = np.zeros(steps)
    mean_freq = np.zeros(steps)

    for t in range(steps):
        # Kuramoto update: theta_dot_i = omega_i + (K / deg_i) * sum_j w_ij sin(theta_j - theta_i)
        dtheta = omega.copy()
        # Sum over edges once; accumulate contributions both ways
        phase_diff = np.sin(theta[edge_j] - theta[edge_i])
        # accumulate to each node
        contrib = np.zeros(N)
        np.add.at(contrib, edge_i, weights * phase_diff)
        np.add.at(contrib, edge_j, -weights * phase_diff)  # antisymmetry
        deg = np.maximum(1.0, np.array([G.degree(k) for k in range(N)], dtype=float))
        dtheta += cfg.K * contrib / deg

        if cfg.noise > 0:
            dtheta += cfg.noise * (rng.standard_normal(N))

        theta += cfg.dt * dtheta
        # order parameter r = |(1/N) sum_k e^{i theta_k}|
        r = np.abs(np.exp(1j * theta).mean())
        order_param[t] = r
        # mean instantaneous frequency
        mean_freq[t] = np.mean(dtheta)

    # Simple “coherence score”
    r_final = float(order_param[-1])
    r_mean = float(order_param[int(0.5 * steps):].mean())

    return {
        "N": N,
        "nx": n_x,
        "ny": n_y,
        "cfg": cfg.__dict__,
        "r_final": r_final,
        "r_mean_late": r_mean,
        "order_param": order_param.tolist(),  # time series
        "mean_freq": mean_freq.tolist(),
    }