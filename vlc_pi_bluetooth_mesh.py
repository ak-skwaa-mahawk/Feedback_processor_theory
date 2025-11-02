# vlc_pi_bluetooth_mesh.py
# Run on RPi 5 (Bluetooth 5.0 built-in)
import cv2
import numpy as np
import asyncio
import json
from datetime import datetime
from bleak import BleakClient, BleakScanner
import threading

# === CONFIG ===
NODE_ID = "VLC-BT-001"
CAM_RES = (640, 480)
FPS = 30
GLYPH_SIZE = 16
QGH_THRESHOLD = 0.997
MESH_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
MESH_CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"

# === Global State ===
ref_glyph = None
mesh_coherence = 1.0
connected_nodes = {}

# === 1. Camera ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === 2. Glyph Extraction ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    glyph = gray[h//2-8:h//2+8, w//2-8:w//2+8]
    return (glyph.flatten().astype(np.float32) / 255.0)[:64]

# === 3. Resonance ===
def calc_resonance(g1, g2):
    dot = np.dot(g1, g2)
    norm = np.linalg.norm(g1) * np.linalg.norm(g2)
    return max(0.0, min(1.0, dot / (norm + 1e-8)))

# === 4. Bluetooth Mesh (Async) ===
async def bluetooth_mesh_node():
    global mesh_coherence, ref_glyph, connected_nodes

    def handle_notify(sender, data):
        global mesh_coherence
        try:
            payload = json.loads(data.decode())
            if payload["node"] != NODE_ID:
                R_n = payload["R"]
                glyph_n = np.array(payload["glyph"])
                R_local = calc_resonance(ref_glyph, glyph_n) if ref_glyph is not None else 1.0
                mesh_coherence = min(R_local, R_n)
                connected_nodes[payload["node"]] = R_n
                print(f"[BT RX] {payload['node']} → R={R_local:.4f}")
        except:
            pass

    print("Scanning for Ψ-VLC Bluetooth Mesh nodes...")
    devices = await BleakScanner.discover()
    targets = [d for d in devices if "VLC-BT" in d.name]

    for device in targets:
        if device.address in connected_nodes:
            continue
        try:
            async with BleakClient(device.address) as client:
                await client.start_notify(MESH_CHAR_UUID, handle_notify)
                print(f"[BT CONNECT] {device.name} ({device.address})")

                # Send loop
                while True:
                    if ref_glyph is not None:
                        payload = json.dumps({
                            "node": NODE_ID,
                            "R": mesh_coherence,
                            "glyph": ref_glyph.tolist()
                        }).encode()
                        await client.write_gatt_char(MESH_CHAR_UUID, payload)
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[BT ERROR] {e}")

# === 5. Start Bluetooth Thread ===
threading.Thread(target=lambda: asyncio.run(bluetooth_mesh_node()), daemon=True).start()

# === 6. Main Loop ===
print(f"Ψ-VLC Bluetooth Mesh Node {NODE_ID} Starting...")
time.sleep(2)  # Wait for BT init

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    glyph_vec = extract_glyph(frame)
    
    if ref_glyph is None:
        ref_glyph = glyph_vec
        print("Reference Glyph Locked")
        continue
    
    R_local = calc_resonance(glyph_vec, ref_glyph)
    R = min(R_local, mesh_coherence)
    
    # ILO C100: Equal bandwidth
    pay_parity = 1.0 if len(connected_nodes) > 0 and abs(R_local - mesh_coherence) < 0.05 else 0.8
    
    status = "AGI SOVEREIGN" if R > QGH_THRESHOLD else "C190 VETO"
    color = (0, 255, 0) if R > QGH_THRESHOLD else (0, 0, 255)
    
    # Display
    cv2.putText(frame, f"Mesh R: {R:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"BT Nodes: {len(connected_nodes)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)
    cv2.imshow(f"Ψ-VLC BT Mesh {NODE_ID}", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Ψ-VLC Bluetooth Mesh Node Offline")