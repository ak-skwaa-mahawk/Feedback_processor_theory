#!/usr/bin/env python3
"""
propagation.py (Acoustic Extension)
----------------------------------
GibberLink RMP with ggwave acoustic encoding for FPT.

* Propagates glyphs as sound waves via ggwave.
* Transmit: Encode gibber → waveform → play.
* Receive: Record → decode → verify coherence.
* Full pipeline: scrape → glyph → acoustic relay.

Author:  John B. Carroll Jr. (prototype implementation)
License: MIT © 2025

Dependencies: pip install ggwave pyaudio networkx numpy scipy
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import hashlib
import time
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import pyaudio  # Audio I/O
import ggwave  # Data-over-sound

# Import FPT siblings (assume in same dir)
from .glyph_generator import generate_glyph
from .scrape_detector import detect_scrape

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
DEFAULT_MAX_HOPS: int = 5
MIN_ENERGY: float = 0.1
COHERENCE_THRESHOLD: float = 0.7
EMBEDDING_DIM: int = 3
SAMPLE_RATE: int = 48000  # ggwave default
PROTOCOL_ID: int = ggwave.ProtocolId.AUDIBLE_FAST  # Audible; use 4 for ultrasonic
VOLUME: int = 20  # 0-100
DURATION_SEC: float = 2.0  # Transmit window

# Audio params
CHUNK_SIZE: int = 4096
FORMAT = pyaudio.paFloat32
CHANNELS = 1


# ----------------------------------------------------------------------
# 2. DATA STRUCTURES (Unchanged from Prior)
# ----------------------------------------------------------------------
@dataclass
class GlyphPacket:
    meta_glyph: str
    gibber_encode: str
    origin_energy: float
    entropy_delta: float
    source_node: str
    timestamp: float = 0.0


@dataclass
class HopLog:
    hop: int
    from_node: str
    to_node: str
    distance: float
    energy_in: float
    energy_out: float
    coherence: float
    status: str
    recovered_glyph: str
    acoustic_success: bool = False  # New: ggwave decode OK?


# ----------------------------------------------------------------------
# 3. ACOUSTIC UTILITIES
# ----------------------------------------------------------------------
class AcousticGibberLink:
    def __init__(self, sample_rate: int = SAMPLE_RATE, protocol: int = PROTOCOL_ID, volume: int = VOLUME):
        self.sample_rate = sample_rate
        self.protocol = protocol
        self.volume = volume
        self.pa = pyaudio.PyAudio()

    def encode_transmit(self, payload: str) -> np.ndarray:
        """Encode gibber payload to waveform and play."""
        # ggwave encode
        gg = ggwave.GGWave()
        try:
            waveform_bytes = gg.encode(payload, self.protocol, self.volume)
            waveform = np.frombuffer(waveform_bytes, dtype=np.float32)
            print(f"Transmitting acoustic glyph: {payload} ({len(waveform)} samples)")
            
            # Play via PyAudio
            stream = self.pa.open(format=FORMAT, channels=CHANNELS, rate=self.sample_rate,
                                  output=True, frames_per_buffer=CHUNK_SIZE)
            stream.write(waveform.tobytes())
            stream.stop_stream()
            stream.close()
            return waveform
        finally:
            gg.free()

    def listen_decode(self, duration: float = DURATION_SEC) -> Optional[str]:
        """Record audio and decode payload."""
        stream = self.pa.open(format=FORMAT, channels=CHANNELS, rate=self.sample_rate,
                              input=True, frames_per_buffer=CHUNK_SIZE)
        
        print("Listening for acoustic glyph...")
        frames = []
        for _ in range(0, int(self.sample_rate / CHUNK_SIZE * duration)):
            data = stream.read(CHUNK_SIZE)
            frames.append(np.frombuffer(data, dtype=np.float32))
        
        stream.stop_stream()
        stream.close()
        
        # Concat and decode
        audio = np.concatenate(frames)
        gg = ggwave.GGWave()
        try:
            decoded_bytes = gg.decode(audio.tobytes())
            if decoded_bytes:
                return decoded_bytes.decode('utf-8')
            return None
        finally:
            gg.free()

    def __del__(self):
        self.pa.terminate()


# ----------------------------------------------------------------------
# 4. CORE PROPAGATION ENGINE (Extended)
# ----------------------------------------------------------------------
class GibberLinkRMP:
    def __init__(
        self,
        graph: nx.Graph,
        acoustic: bool = True,  # New: Enable ggwave
        embedding_func=None,
        max_hops: int = DEFAULT_MAX_HOPS,
        min_energy: float = MIN_ENERGY,
        coherence_threshold: float = COHERENCE_THRESHOLD,
        sample_rate: int = SAMPLE_RATE,
    ):
        self.graph = graph
        self.acoustic = acoustic
        self.acoustic_link = AcousticGibberLink(sample_rate) if acoustic else None
        self.max_hops = max_hops
        self.min_energy = min_energy
        self.coherence_threshold = coherence_threshold
        self.embedding_func = embedding_func or self._default_embedding

    def _default_embedding(self, node: str) -> np.ndarray:
        h = hashlib.md5(node.encode()).digest()
        return np.array([b / 255.0 for b in h[:EMBEDDING_DIM]])

    def _compute_coherence(self, node_a: str, node_b: str) -> float:
        vec_a = self.embedding_func(node_a)
        vec_b = self.embedding_func(node_b)
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b) + 1e-8))

    def _isst_decay(self, energy: float, distance: float) -> float:
        return max(self.min_energy, energy / (distance ** 2))

    def _acoustic_relay(self, payload: str, to_node: str) -> bool:
        """Simulate/sim actual acoustic tx/rx between nodes."""
        if not self.acoustic:
            return True  # Fallback to simulated
        waveform = self.acoustic_link.encode_transmit(payload)
        time.sleep(0.5)  # Propagation delay
        decoded = self.acoustic_link.listen_decode()
        success = decoded == payload
        print(f"Acoustic relay to {to_node}: {'OK' if success else 'ERR'} (decoded: {decoded})")
        return success

    def propagate(
        self,
        packet: GlyphPacket,
        start_node: str,
    ) -> Dict[str, List[HopLog]]:
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

                dist = self.graph[current_node][neighbor].get("weight", 1.0)
                energy_out = self._isst_decay(energy_in, dist)
                coherence = self._compute_coherence(current_node, neighbor)

                status = "DECAYED"
                recovered = "❌"
                acoustic_success = False
                if coherence >= self.coherence_threshold and energy_out > self.min_energy:
                    # Acoustic relay
                    acoustic_success = self._acoustic_relay(pkt.gibber_encode, neighbor)
                    if acoustic_success:
                        recovered = pkt.meta_glyph
                        status = f"GIBBERLINK ACOUSTIC: {pkt.gibber_encode}"
                        queue.append((neighbor, pkt, hop + 1, energy_out * 0.95))
                    else:
                        status = "ACOUSTIC FAIL"
                        recovered = "❌"

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
                    acoustic_success=acoustic_success,
                )
                log[neighbor].append(hop_log)

        return log


# ----------------------------------------------------------------------
# 5. HIGH-LEVEL API (Unchanged; Uses New Acoustic)
# ----------------------------------------------------------------------
def full_fpt_pipeline(
    signal_pre: np.ndarray,
    signal_post: np.ndarray,
    graph: nx.Graph,
    source_node: str,
    acoustic: bool = True,
    **detect_kwargs,
) -> Tuple[Dict[str, Any], Dict[str, List[HopLog]]]:
    scrape = detect_scrape(signal_pre, signal_post, **detect_kwargs)
    if not scrape["is_scrape"]:
        raise ValueError("No scrape detected — nothing to propagate")

    glyph = generate_glyph(scrape["decay_signal"], scrape["entropy_delta"])

    packet = GlyphPacket(
        meta_glyph=glyph["meta_glyph"],
        gibber_encode=glyph["gibber_encode"],
        origin_energy=scrape["decay_signal"],
        entropy_delta=scrape["entropy_delta"],
        source_node=source_node,
    )

    rmp = GibberLinkRMP(graph, acoustic=acoustic)
    prop_log = rmp.propagate(packet, source_node)

    return scrape, prop_log


# ----------------------------------------------------------------------
# 6. DEMO: Acoustic Handshake in Drone Mesh
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Mesh: Source → Media nodes → Flamevault
    G = nx.Graph()
    nodes = ["Source", "Meta", "Sephora", "FoxNews", "Flamevault"]
    edges = [
        ("Source", "Meta", {"weight": 1.0}),
        ("Meta", "Sephora", {"weight": 1.5}),
        ("Meta", "FoxNews", {"weight": 1.8}),
        ("Sephora", "Flamevault", {"weight": 2.0}),
        ("FoxNews", "Flamevault", {"weight": 2.2}),
    ]
    G.add_edges_from(edges)
    for n in nodes:
        G.add_node(n)

    # Sephora scrape sim
    t = np.linspace(0, 10, 200)
    pre = np.sin(t)
    post = pre.copy()
    post[80:120] += 1.2 * np.random.randn(40)

    try:
        scrape, prop_log = full_fpt_pipeline(
            pre, post,
            graph=G,
            source_node="Source",
            acoustic=True,  # Enable ggwave
            initial_energy=15.0,
            distance=1.0,
        )
        print("Scrape Event:")
        print(f"  ΔH = {scrape['entropy_delta']:.3f}, Energy = {scrape['decay_signal']:.2f}")
        print(f"  Glyph: {scrape['description']}")

        print("\nAcoustic Propagation Summary:")
        for node, hops in prop_log.items():
            if hops:
                final = hops[-1]
                print(f"  {node:10} ← {final.status} | {final.recovered_glyph} (E={final.energy_out:.2f}, Acoustic: {final.acoustic_success})")

        # Visual: Mesh with acoustic status
        pos = nx.spring_layout(G, seed=42)
        colors = ['cyan' if h.acoustic_success else 'red' for hops in prop_log.values() for h in hops[-1:] if hops]
        colors = colors[:len(nodes)]  # Truncate
        nx.draw(G, pos, node_color=colors, with_labels=True, node_size=2000, font_size=10)
        plt.title("Acoustic GibberLink RMP: Sonic Handshake Return")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("Pipeline failed:", e)
        # Fallback sim without audio
        _, prop_log = full_fpt_pipeline(pre, post, G, "Source", acoustic=False)
        print("Fallback sim log:", prop_log)


# ----------------------------------------------------------------------
# 7. UNIT TESTS (Extended)
# ----------------------------------------------------------------------
import unittest


class TestAcousticPropagation(unittest.TestCase):
    def setUp(self):
        self.G = nx.path_graph(3)  # 0-1-2
        for u, v in self.G.edges():
            self.G[u][v]["weight"] = 1.0

    def test_acoustic_encode_decode(self):
        # Test ggwave roundtrip (no audio)
        gg = ggwave.GGWave()
        try:
            payload = "A1B2C3D4"
            waveform_bytes = gg.encode(payload, ggwave.ProtocolId.AUDIBLE_FAST, 20)
            decoded = gg.decode(waveform_bytes)
            self.assertEqual(decoded.decode('utf-8'), payload)
        finally:
            gg.free()

    # Prior tests unchanged...
    def test_propagation_success(self):
        packet = GlyphPacket("🔥🧬", "A1B2C3D4", 10.0, 0.05, "0")
        rmp = GibberLinkRMP(self.G, acoustic=False)  # Sim mode for test
        log = rmp.propagate(packet, "0")
        self.assertIn("2", log)
        self.assertTrue(any("GIBBERLINK" in h.status for h in log["2"]))


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
import ggwave
gg = ggwave.GGWave()
try:
    wf = gg.encode("A1B2C3D4", ggwave.ProtocolId.AUDIBLE_FAST, 20)
    decoded = gg.decode(wf)
    print(decoded.decode('utf-8'))  # → A1B2C3D4
finally:
    gg.free()
