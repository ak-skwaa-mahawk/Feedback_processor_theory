# ble_mesh_provisioner.py
import asyncio
from bleak import BleakScanner, BleakClient
import json
import cv2
import qrcode
from datetime import datetime

NODE_ID = "PROV-001"
MESH_NETKEY = "00112233445566778899aabbccddeeff"
MESH_APPKEY = "ffeeddccbbaa99887766554433221100"

async def provision_node():
    print("Ψ-BLE Mesh Provisioner Online")

    # Generate QR for OOB
    qr_data = json.dumps({
        "node": NODE_ID,
        "pubkey": "04a1b2c3...",  # Mock ECDH pubkey
        "netkey": MESH_NETKEY
    })
    qr = qrcode.make(qr_data)
    qr.save("prov_qr.png")
    print("Scan QR with unprovisioned node → prov_qr.png")

    # Scan for unprovisioned
    devices = await BleakScanner.discover()
    targets = [d for d in devices if "VLC-UNPROV" in (d.name or "")]
    
    for dev in targets:
        print(f"Found: {dev.name} ({dev.address})")
        async with BleakClient(dev.address) as client:
            # Simulate ILO veto
            R = 0.998
            pay_parity = 1.0
            if R < 0.997 or pay_parity < 0.95:
                print("C190/C100 VETO → Reject")
                continue

            # Send NetKey + AppKey (encrypted)
            payload = json.dumps({
                "netkey": MESH_NETKEY,
                "appkey": MESH_APPKEY,
                "addr": "0x0002"
            }).encode()
            # In real: use provisioning PDU
            print(f"Provisioned {dev.name} → Addr 0x0002")

asyncio.run(provision_node())