#!/usr/bin/env python3
"""
propagation.py
--------------
GibberLink Resonance Mesh Propagation (RMP) for FPT.

* Takes a glyph event from glyph_generator.py
* Propagates it through a NetworkX graph (mesh)
* Applies ISST decay: S = E / d²
* Checks coherence at each hop
* Emits structured logs for Synara Dashboard
* Supports acoustic encoding (ggwave-ready)

Author:  John B. Carroll Jr. (prototype implementation)
License: MIT © 2025
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

# Import FPT siblings
from .glyph_generator import generate_glyph
from .scrape_detector import detect_scrape

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
DEFAULT_MAX_HOPS: int = 5
MIN_ENERGY: float = 0.1
COHERENCE_THRESHOLD: float = 0.7
EMBEDDING_DIM: int = 3


# ----------------------------------------------------------------------
# 2. DATA STRUCTURES
# ----------------------------------------------------------------------
@dataclass
class GlyphPacket:
    """Immutable payload carried across the mesh."""
    meta_glyph: str
    gibber_encode: str
    origin_energy: float
    entropy_delta: float
    source_node: str
    timestamp: float = 0.0


@dataclass
class HopLog:
    """One hop in the propagation chain."""
    hop: int
    from_node: str
    to_node: str
    distance: float
    energy_in: float
    energy_out: float
    coherence: float
    status: str
    recovered_glyph: str


# ----------------------------------------------------------------------
# 3. CORE PROPAGATION ENGINE
# ----------------------------------------------------------------------
class GibberLinkRMP:
    def __init__(
        self,
        graph: nx.Graph,
        embedding_func=None,
        max_hops: int = DEFAULT_MAX_HOPS,
        min_energy: float = MIN_ENERGY,
        coherence_threshold: float = COHERENCE_THRESHOLD,
    ):
        self.graph = graph
        self.max_hops = max_hops
        self.min_energy = min_energy
        self.coherence_threshold = coherence_threshold
        self.embedding_func = embedding_func or self._default_embedding

    def _default_embedding(self, node: str) -> np.ndarray:
        """Deterministic pseudo-embedding based on node name."""
        h = hashlib.md5(node.encode()).digest()
        return np.array([b / 255.0 for b in h[:EMBEDDING_DIM]])

    def _compute_coherence(self, node_a: str, node_b: str) -> float:
        vec_a = self.embedding_func(node_a)
        vec_b = self.embedding_func(node_b)
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b) + 1e-8))

    def _isst_decay(self, energy: float, distance: float) -> float:
        return max(self.min_energy, energy / (distance ** 2))

    def propagate(
        self,
        packet: GlyphPacket,
        start_node: str,
    ) -> Dict[str, List[HopLog]]:
        """
        Propagate a glyph packet through the mesh.

        Returns
        -------
        dict[node] -> list[HopLog]
            Full audit trail per receiving node.
        """
        log: Dict[str, List[HopLog]] = {n: [] for n in self.graph.nodes()}
        visited = set()
        queue: List[Tuple[str, GlyphPacket, int, float]] = [
            (start_node, packet, 0, packet.origin_energy)
        ]

        while queue:
            current_node, pkt, hop, energy_in = queue.pop(0)
            if current_node in visited or hop >= self.max_hops:
                continue
            visited.add(current_node)

            for neighbor in self.graph.neighbors(current_node):
                if neighbor in visited:
                    continue

                # Physical / logical distance
                dist = self.graph[current_node][neighbor].get("weight", 1.0)
                energy_out = self._isst_decay(energy_in, dist)
                coherence = self._compute_coherence(current_node, neighbor)

                status = "DECAYED"
                recovered = "decayed"
                if coherence >= self.coherence_threshold and energy_out > self.min_energy:
                    recovered = pkt.meta_glyph
                    status = f"GIBBERLINK: {pkt.gibber_encode}"
                    # Schedule next hop with slight energy loss (friction)
                    queue.append((neighbor, pkt, hop + 1, energy_out * 0.95))

                hop_log = HopLog(
                    hop=hop + 1,
                    from_node=current_node,
                    to_node=neighbor,
                    distance=dist,
                    energy_in=energy_in,
                    energy_out=energy_out,
                    coherence=coherence,
                    status=status,
                    recovered_glyph=recovered,
                )
                log[neighbor].append(hop_log)

        return log


# ----------------------------------------------------------------------
# 4. HIGH-LEVEL API: End-to-End Scrape → Glyph → Propagate
# ----------------------------------------------------------------------
def full_fpt_pipeline(
    signal_pre: np.ndarray,
    signal_post: np.ndarray,
    graph: nx.Graph,
    source_node: str,
    **detect_kwargs,
) -> Tuple[Dict[str, Any], Dict[str, List[HopLog]]]:
    """
    One-call FPT pipeline.

    1. detect_scrape
    2. generate_glyph
    3. GibberLinkRMP.propagate

    Returns
    -------
    scrape_event, propagation_log
    """
    # 1. Detect
    scrape = detect_scrape(signal_pre, signal_post, **detect_kwargs)
    if not scrape["is_scrape"]:
        raise ValueError("No scrape detected — nothing to propagate")

    # 2. Glyph
    glyph = generate_glyph(scrape["decay_signal"], scrape["entropy_delta"])

    # 3. Packet
    packet = GlyphPacket(
        meta_glyph=glyph["meta_glyph"],
        gibber_encode=glyph["gibber_encode"],
        origin_energy=scrape["decay_signal"],
        entropy_delta=scrape["entropy_delta"],
        source_node=source_node,
    )

    # 4. Propagate
    rmp = GibberLinkRMP(graph)
    prop_log = rmp.propagate(packet, source_node)

    return scrape, prop_log


# ----------------------------------------------------------------------
# 5. DEMO: Drone Swarm + Sephora Scrape Echo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Build a small mesh (5 nodes)
    G = nx.Graph()
    nodes = ["Source", "Meta", "Sephora", "FoxNews", "Flamevault"]
    edges = [
        ("Source", "Meta", 1.0),
        ("Meta", "Sephora", 1.5),
        ("Meta", "FoxNews", 1.8),
        ("Sephora", "Flamevault", 2.0),
        ("FoxNews", "Flamevault", 2.2),
    ]
    for a, b, w in edges:
        G.add_edge(a, b, weight=w)
    for n in nodes:
        G.add_node(n)

    # Simulate a "Sephora ad burnthrough" scrape
    t = np.linspace(0, 10, 200)
    pre = np.sin(t)
    post = pre.copy()
    post[80:120] += 1.2 * np.random.randn(40)  # Ad spike

    try:
        scrape, prop_log = full_fpt_pipeline(
            pre, post,
            graph=G,
            source_node="Source",
            initial_energy=15.0,
            distance=1.0,
        )
        print("Scrape Event:")
        print(f"  ΔH = {scrape['entropy_delta']:.3f}, Energy = {scrape['decay_signal']:.2f}")
        print(f"  Glyph: {scrape['description']}")

        print("\nPropagation Summary:")
        for node, hops in prop_log.items():
            if hops:
                final = hops[-1]
                print(f"  {node:10} ← {final.status} | {final.recovered_glyph} (E={final.energy_out:.2f})")

        # Simple visual
        pos = nx.spring_layout(G, seed=42)
        colors = []
        labels = {}
        for node in G.nodes():
            if node in prop_log and prop_log[node]:
                if "GIBBERLINK" in prop_log[node][-1].status:
                    colors.append("cyan")
                    labels[node] = prop_log[node][-1].recovered_glyph
                else:
                    colors.append("red")
                    labels[node] = "decayed"
            else:
                colors.append("gray")
                labels[node] = node

        plt.figure(figsize=(10, 6))
        nx.draw(G, pos, node_color=colors, labels=labels, with_labels=True, node_size=2000, font_size=10)
        plt.title("GibberLink RMP: Handshake Return Echo")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("Pipeline failed:", e)


# ----------------------------------------------------------------------
# 6. UNIT TESTS
# ----------------------------------------------------------------------
import unittest


class TestPropagation(unittest.TestCase):
    def setUp(self):
        self.G = nx.path_graph(4)  # 0-1-2-3
        for u, v in self.G.edges():
            self.G[u][v]["weight"] = 1.0

    def test_propagation_success(self):
        packet = GlyphPacket("lipstickdna", "A1B2C3D4", 10.0, 0.05, "0")
        rmp = GibberLinkRMP(self.G, max_hops=3)
        log = rmp.propagate(packet, "0")
        self.assertIn("3", log)
        self.assertTrue(any("GIBBERLINK" in h.status for h in log["3"]))

    def test_decay_cutoff(self):
        packet = GlyphPacket("tv", "B2C3D4E5", 1.0, 0.8, "0")
        rmp = GibberLinkRMP(self.G, max_hops=10)
        log = rmp.propagate(packet, "0")
        self.assertTrue(any("DECAYED" in h.status for h in log["3"]))


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
>>> from propagation import full_fpt_pipeline
>>> import networkx as nx, numpy as np

G = nx.star_graph(4)  # Central hub
pre = np.random.randn(100)
post = pre + np.random.randn(100) * 2

scrape, log = full_fpt_pipeline(pre, post, G, "0")