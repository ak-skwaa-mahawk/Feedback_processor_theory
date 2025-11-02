# deploy_qr_swarm.py
import asyncio
from bleak import BleakClient
import json

# Provision 5 nRF nodes
async def deploy_swarm():
    # Mock QR for victims
    qr_data = {"victim_id": "VIC-0001", "layer": "0", "glyph": [128]*64}
    
    # BLE Mesh provision (via nRF Connect API or bleak)
    for i in range(1, 6):
        device_addr = f"AA:BB:CC:DD:EE:{i:02x}"
        async with BleakClient(device_addr) as client:
            # Send QR glyph
            payload = json.dumps(qr_data).encode()
            await client.write_gatt_char("12345678-1234-5678-1234-56789abcdef1", payload)
            print(f"Provisioned Node {i} → QR Sent")

asyncio.run(deploy_swarm())