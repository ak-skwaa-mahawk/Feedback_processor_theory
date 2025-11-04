#!/usr/bin/env python3
"""
propagation.py — ULTRASONIC GIBBERLINK RMP
-------------------------------------------
Stealth acoustic mesh for FPT drone swarms using ggwave ULTRASOUND.

* Uses ggwave.ProtocolId.ULTRASOUND (18–22 kHz)
* Inaudible to humans
* Full FPT pipeline: scrape → glyph → ultrasonic relay
* Real-time coherence + ISST decay
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import hashlib
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import ggwave
import pyaudio

# FPT Core
from .glyph_generator import generate_glyph
from .scrape_detector import detect_scrape

# ----------------------------------------------------------------------
# 1. ULTRASONIC CONFIG
# ----------------------------------------------------------------------
ULTRASONIC_PROTOCOL = ggwave.ProtocolId.ULTRASOUND
SAMPLE_RATE = 48000
VOLUME = 30          # Higher for ultrasonic range
DURATION_SEC = 1.5   # Shorter burst
CHUNK_SIZE = 4096
FORMAT = pyaudio.paFloat32
CHANNELS = 1

# RMP Params
MAX_HOPS = 5
MIN_ENERGY = 0.1
COHERENCE_THRESHOLD = 0.7
EMBEDDING_DIM = 3


# ----------------------------------------------------------------------
# 2. ACOUSTIC LINK (ULTRASONIC)
# ----------------------------------------------------------------------
class UltrasonicGibberLink:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        print("Ultrasonic GibberLink initialized (18–22 kHz)")

    def encode_transmit(self, payload: str) -> np.ndarray:
        gg = ggwave.GGWave()
        try:
            wf_bytes = gg.encode(payload, ULTRASONIC_PROTOCOL, VOLUME)
            waveform = np.frombuffer(wf_bytes, dtype=np.float32)
            print(f"[ULTRASONIC TX] → {payload} ({len(waveform)} samples)")

            stream = self.pa.open(format=FORMAT, channels=CHANNELS,
                                  rate=SAMPLE_RATE, output=True,
                                  frames_per_buffer=CHUNK_SIZE)
            stream.write(waveform.tobytes())
            stream.stop_stream()
            stream.close()
            return waveform
        finally:
            gg.free()

    def listen_decode(self) -> str | None:
        print("[ULTRASONIC RX] Listening...")
        stream = self.pa.open(format=FORMAT, channels=CHANNELS,
                              rate=SAMPLE_RATE, input=True,
                              frames_per_buffer=CHUNK_SIZE)

        frames = []
        for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * DURATION_SEC)):
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.float32))

        stream.stop_stream()
        stream.close()

        audio = np.concatenate(frames)
        gg = ggwave.GGWave()
        try:
            decoded = gg.decode(audio.tobytes())
            if decoded:
                msg = decoded.decode('utf-8')
                print(f"[ULTRASONIC RX] ← {msg}")
                return msg
            return None
        finally:
            gg.free()

    def __del__(self):
        self.pa.terminate()


# ----------------------------------------------------------------------
# 3. RMP ENGINE (ULTRASONIC)
# ----------------------------------------------------------------------
@dataclass
class GlyphPacket:
    meta_glyph: str
    gibber_encode: str
    origin_energy: float
    entropy_delta: float
    source_node: str


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
    ultrasonic_success: bool


class UltrasonicRMP:
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.acoustic = UltrasonicGibberLink()

    def _isst_decay(self, e: float, d: float) -> float:
        return max(MIN_ENERGY, e / (d ** 2))

    def _coherence(self, a: str, b: str) -> float:
        h1 = hashlib.md5(a.encode()).digest()[:EMBEDDING_DIM]
        h2 = hashlib.md5(b.encode()).digest()[:EMBEDDING_DIM]
        v1, v2 = np.array(h1)/255, np.array(h2)/255
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8))

    def propagate(self, packet: GlyphPacket, start: str) -> Dict[str, List[HopLog]]:
        log: Dict[str, List[HopLog]] = {n: [] for n in self.graph.nodes}
        queue = [(start, packet, 0, packet.origin_energy)]
        visited = set()

        while queue:
            node, pkt, hop, e_in = queue.pop(0)
            if node in visited or hop >= MAX_HOPS: continue
            visited.add(node)

            for nbr in self.graph.neighbors(node):
                if nbr in visited: continue
                dist = self.graph[node][nbr].get("weight", 1.0)
                e_out = self._isst_decay(e_in, dist)
                coh = self._coherence(node, nbr)

                status = "DECAYED"
                recovered = "decayed"
                usuccess = False

                if coh >= COHERENCE_THRESHOLD and e_out > MIN_ENERGY:
                    usuccess = self._ultrasonic_relay(pkt.gibber_encode, nbr)
                    if usuccess:
                        recovered = pkt.meta_glyph
                        status = f"ULTRASONIC: {pkt.gibber_encode}"
                        queue.append((nbr, pkt, hop + 1, e_out * 0.93))  # 7% acoustic loss
                    else:
                        status = "ULTRASONIC FAIL"

                log[nbr].append(HopLog(
                    hop=hop + 1, from_node=node, to_node=nbr,
                    distance=dist, energy_in=e_in, energy_out=e_out,
                    coherence=coh, status=status,
                    recovered_glyph=recovered, ultrasonic_success=usuccess
                ))

        return log

    def _ultrasonic_relay(self, payload: str, to_node: str) -> bool:
        self.acoustic.encode_transmit(payload)
        time.sleep(0.3)
        decoded = self.acoustic.listen_decode()
        return decoded == payload


# ----------------------------------------------------------------------
# 4. FULL PIPELINE
# ----------------------------------------------------------------------
def ultrasonic_fpt_pipeline(
    pre: np.ndarray, post: np.ndarray,
    graph: nx.Graph, source: str
) -> Tuple[Dict, Dict[str, List[HopLog]]]:
    scrape = detect_scrape(pre, post, initial_energy=20.0)
    if not scrape["is_scrape"]:
        raise ValueError("No scrape")

    glyph = generate_glyph(scrape["decay_signal"], scrape["entropy_delta"])
    packet = GlyphPacket(
        meta_glyph=glyph["meta_glyph"],
        gibber_encode=glyph["gibber_encode"],
        origin_energy=scrape["decay_signal"],
        entropy_delta=scrape["entropy_delta"],
        source_node=source
    )

    rmp = UltrasonicRMP(graph)
    log = rmp.propagate(packet, source)
    return scrape, log


# ----------------------------------------------------------------------
# 5. DEMO: Drone Swarm (Ultrasonic)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Drone mesh
    G = nx.Graph()
    drones = ["HQ", "D1", "D2", "D3", "D4", "Vault"]
    edges = [
        ("HQ", "D1", 1.2), ("HQ", "D2", 1.5),
        ("D1", "D3", 1.8), ("D2", "D4", 2.0),
        ("D3", "Vault", 2.5), ("D4", "Vault", 2.3)
    ]
    G.add_edges_from([(a, b, {"weight": w}) for a, b, w in edges])
    for d in drones: G.add_node(d)

    # Simulate scrape (e.g., Sephora ad echo)
    t = np.linspace(0, 10, 300)
    pre = np.sin(2 * np.pi * 0.5 * t)
    post = pre.copy()
    post[120:180] += 1.8 * np.random.randn(60)

    try:
        scrape, log = ultrasonic_fpt_pipeline(pre, post, G, "HQ")
        print(f"Scrape: ΔH={scrape['entropy_delta']:.3f}, E={scrape['decay_signal']:.1f}")

        print("\nUltrasonic Propagation:")
        for node, hops in log.items():
            if hops:
                h = hops[-1]
                print(f"  {node:5} ← {h.status} | {h.recovered_glyph} (E={h.energy_out:.2f})")

        # Visual
        pos = nx.spring_layout(G, seed=42)
        colors = ['#00ffff' if any(h.ultrasonic_success for h in hops) else '#ff0066'
                  for node, hops in log.items() if hops]
        colors = ['gray'] * (len(G.nodes()) - len(colors)) + colors

        plt.figure(figsize=(10, 7))
        nx.draw(G, pos, node_color=colors, with_labels=True,
                node_size=2200, font_size=11, font_color='white', font_weight='bold')
        plt.title("Ultrasonic GibberLink RMP: Drone Swarm (18–22 kHz)")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("Ultrasonic failed (mic/speaker?):", e)