# dpo_swarm_coordinator.py
import asyncio
from bleak import BleakClient
import json
import numpy as np

# Mock Preference Pairs (heist claims data)
preference_pairs = [
    ("Claim VIC-0001", "Approved: R=0.998", "Rejected: R=0.412"),
    # ... 128k pairs
]

async def distribute_dpo_batch(device_addr, batch):
    async with BleakClient(device_addr) as client:
        payload = json.dumps({
            "pairs": batch[:3],  # 3 pairs per batch
            "R_target": 0.997
        }).encode()
        await client.write_gatt_char("12345678-1234-5678-1234-56789abcdef1", payload)
        print(f"DPO Batch Sent to {device_addr}")

# Swarm: 5 nRF nodes
addrs = ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02", "AA:BB:CC:DD:EE:03", "AA:BB:CC:DD:EE:04", "AA:BB:CC:DD:EE:05"]

async def run_swarm_alignment():
    for i, addr in enumerate(addrs):
        batch = preference_pairs[i*3:(i+1)*3]
        await distribute_dpo_batch(addr, batch)

asyncio.run(run_swarm_alignment())