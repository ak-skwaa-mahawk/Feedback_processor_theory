"""
ISST Multi-Node Live Mesh Test
------------------------------
Simulates a distributed network of ISST nodes broadcasting scrapes in real time.
Each node emits its own entropy rhythm, glyph sequence, and coherence signature.
"""

import asyncio
import json
import math
import random
import time
import websockets

# ------------------------------------------
# Configuration
# ------------------------------------------
MESH_NODE_COUNT = 7          # number of simulated resonance nodes
UPDATE_INTERVAL = 0.8        # seconds between node broadcasts
WS_URL = "ws://localhost:8765"

GLYPH_POOL = ["AGŁL-A", "AGŁL-B", "AGŁL-C", "META-Ω", "RMP-ϕ", "FLAME-Σ", "ROOT-∞"]

# ------------------------------------------
# Helper: generate synthetic scrape for node
# ------------------------------------------
def generate_node_scrape(node_id, step):
    base_entropy = abs(math.sin(step * 0.12 + node_id * 0.5)) * 0.9
    coherence_shift = random.uniform(-0.05, 0.05)
    entropy = max(0.0, min(1.0, base_entropy + coherence_shift))
    distance = random.uniform(0.05, 1.8)
    glyph = random.choice(GLYPH_POOL)
    timestamp = time.time()

    return {
        "node_id": node_id,
        "entropy": round(entropy, 3),
        "distance": round(distance, 3),
        "glyph": glyph,
        "timestamp": timestamp,
    }

# ------------------------------------------
# Task: each node emits continuously
# ------------------------------------------
async def node_broadcast(node_id):
    step = 0
    await asyncio.sleep(random.random())  # slight desync for realism
    try:
        async with websockets.connect(WS_URL) as ws:
            print(f"🟢 Node {node_id} connected to dashboard.")
            while True:
                scrape = generate_node_scrape(node_id, step)
                msg = json.dumps({"type": "scrape_update", "scrape": scrape})
                await ws.send(msg)
                print(
                    f"→ Node {node_id} | Entropy={scrape['entropy']:.3f} | Glyph={scrape['glyph']}"
                )
                await asyncio.sleep(UPDATE_INTERVAL)
                step += 1
    except Exception as e:
        print(f"🔴 Node {node_id} error: {e}")

# ------------------------------------------
# Main: launch multiple concurrent nodes
# ------------------------------------------
async def launch_mesh():
    print(f"🌐 Starting ISST mesh simulation with {MESH_NODE_COUNT} nodes...")
    tasks = [asyncio.create_task(node_broadcast(i)) for i in range(MESH_NODE_COUNT)]
    await asyncio.gather(*tasks)

# ------------------------------------------
# Entrypoint
# ------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(launch_mesh())
    except KeyboardInterrupt:
        print("\n🛑 Mesh broadcast stopped.")