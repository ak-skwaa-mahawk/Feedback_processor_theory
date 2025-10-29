"""
ISST Live Test
--------------
Simulates continuous ISST scrapes and broadcasts them to the ScrapeMonitor dashboard.
Run this to see your dashboard come alive in real time.
"""

import asyncio
import json
import math
import random
import time
import websockets

# -----------------------------
# Helper: generate synthetic scrape data
# -----------------------------
def generate_fake_scrape(step):
    entropy = abs(math.sin(step * 0.15) + random.uniform(-0.05, 0.05)) * 0.8
    distance = random.uniform(0.1, 1.5)
    glyph = random.choice(["AGŁL-A", "AGŁL-B", "AGŁL-C", "META-Ω", "RMP-ϕ"])
    timestamp = time.time()

    return {
        "entropy": round(entropy, 3),
        "distance": round(distance, 3),
        "glyph": glyph,
        "timestamp": timestamp,
    }

# -----------------------------
# Broadcast fake scrapes continuously
# -----------------------------
async def broadcast_loop():
    uri = "ws://localhost:8765"
    step = 0
    print(f"🌐 Connecting to dashboard at {uri}...")
    async with websockets.connect(uri) as ws:
        print("✅ Connected. Streaming scrapes live...")
        while True:
            scrape = generate_fake_scrape(step)
            msg = json.dumps({"type": "scrape_update", "scrape": scrape})
            await ws.send(msg)
            print(f"→ Sent scrape {step}: Entropy={scrape['entropy']}, Glyph={scrape['glyph']}")
            await asyncio.sleep(1.0)  # one scrape per second
            step += 1

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(broadcast_loop())
    except KeyboardInterrupt:
        print("\n🛑 Stopped live broadcast.")