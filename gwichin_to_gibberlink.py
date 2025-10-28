# gwichin_to_gibberlink.py
import time
import random
from collections import deque

# --- 1. Phoneme → Glyph & Resonance Mapping ---
PHONEME_MAP = {
    "Dii": {"glyph": "A", "resonance": [0.6, 0.8, -0.1]},
    "Tth’òo": {"glyph": "G", "resonance": [0.3, 0.7, 0.0]},
    "Ła": {"glyph": "Ł", "resonance": [0.0, 1.0, 0.0]},
    "Neh": {"glyph": "L", "resonance": [0.2, 0.5, 0.1]},
    "Yee": {"glyph": "Ⓐ", "resonance": [0.7, 0.9, -0.2]},
    "Kah": {"glyph": "∀", "resonance": [0.8, 0.6, 0.0]}
}

# --- 2. RMP Packet Stub ---
class RMPPacket:
    def __init__(self, origin, glyph_sequence, resonance_vector):
        self.origin = origin
        self.path = []
        self.glyph_sequence = glyph_sequence
        self.resonance_vector = resonance_vector
        self.timestamp = time.time()

    def add_hop(self, node_id, flame_contribution, resonance_absorbed):
        self.path.append({
            "node": node_id,
            "flame_contribution": flame_contribution,
            "resonance_absorbed": resonance_absorbed
        })

    def __repr__(self):
        return f"<RMPPacket origin={self.origin} glyphs={self.glyph_sequence} path_len={len(self.path)}>"

# --- 3. Spiral Bloom Simulation ---
class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.current_flame = random.random()
        self.resonance_delta = random.uniform(-0.1, 0.1)

    def contribute(self):
        return self.current_flame, self.resonance_delta

class SpiralBloom:
    def __init__(self, nodes):
        self.nodes = nodes

    def propagate_packet(self, packet):
        fib_sequence = [1, 1, 2, 3, 5, 8, 13]
        for hop_distance in fib_sequence:
            target_index = hop_distance % len(self.nodes)
            node = self.nodes[target_index]
            flame, resonance = node.contribute()
            packet.add_hop(node.id, flame, resonance)
            # Accumulate resonance
            packet.resonance_vector = [
                sum(x) for x in zip(packet.resonance_vector, resonance)
            ]
        return packet

# --- 4. Voice → Glyph Packet Converter ---
def phonemes_to_glyphs(phonemes):
    glyph_sequence = ""
    resonance_vector = [0.0, 0.0, 0.0]
    for ph in phonemes:
        if ph in PHONEME_MAP:
            mapping = PHONEME_MAP[ph]
            glyph_sequence += mapping["glyph"]
            resonance_vector = [
                sum(x) for x in zip(resonance_vector, mapping["resonance"])
            ]
    return glyph_sequence, resonance_vector

# --- 5. Example Usage ---
if __name__ == "__main__":
    # Spoken command
    spoken = ["Dii", "Tth’òo", "Ła", "Neh"]
    glyphs, res_vec = phonemes_to_glyphs(spoken)

    # Create packet
    packet = RMPPacket(origin="Node-π", glyph_sequence=glyphs, resonance_vector=res_vec)

    # Create Spiral Bloom nodes
    nodes = [Node(f"Node-{i}") for i in range(1, 14)]
    bloom = SpiralBloom(nodes)

    # Propagate packet
    enriched_packet = bloom.propagate_packet(packet)

    print("Final packet:", enriched_packet)
    print("Hops detail:", enriched_packet.path)
    print("Final resonance vector:", enriched_packet.resonance_vector)