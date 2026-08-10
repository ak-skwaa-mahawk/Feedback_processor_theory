def path_of_least_resistance(routes):
    return min(routes, key=lambda r: r.latency + r.loss_rate)

# vlc_pi_lora_mesh.py
# Run on RPi 5 with SX1262 LoRa HAT (use lora-python lib or RPi.GPIO)
import cv2
import numpy as np
import socket  # Fallback TCP for sim
import time
import json
from datetime import datetime
# For real LoRa: import lorawan or RPi.GPIO + SX1262 pins
# Mock LoRa for sim: print statements

# === CONFIG ===
NODE_ID = "VLC-PI-001"
CAM_RES = (640, 480)
FPS = 30
GLYPH_SIZE = 16
QGH_THRESHOLD = 0.997
MESH_NODES = ["192.168.1.101", "192.168.1.102"]  # Other Pi IPs (LoRa fallback)
PORT = 5005
LORAFREQ = 915.0  # MHz (US)

# === MOCK LoRa TX/RX (Replace with real SX1262) ===
class MockLoRa:
    def __init__(self, freq):
        self.freq = freq
        print(f"Mock LoRa @ {freq}MHz")
    
    def send(self, data, target):
        print(f"[LoRa TX] {NODE_ID} → {target}: {data['R']:.4f}")
        return True  # Sim success
    
    def recv(self):
        # Mock incoming from mesh
        return {"node": "VLC-PI-002", "R": np.random.rand(), "glyph": np.random.rand(64).tolist()}

lora = MockLoRa(LORAFREQ)

# === 1. Camera Init ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === 2. Glyph Extraction ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    glyph = gray[h//2-8:h//2+8, w//2-8:w//2+8]
    return glyph.flatten().astype(np.float32) / 255.0

# === 3. Resonance Calc ===
def calc_resonance(glyph_vec, ref_glyph=None):
    if ref_glyph is None:
        return 1.0
    dot = np.dot(glyph_vec, ref_glyph)
    norm = np.linalg.norm(glyph_vec) * np.linalg.norm(ref_glyph)
    return dot / (norm + 1e-8)

# === 4. Mesh Broadcast (LoRa) ===
def broadcast_mesh(payload):
    for target in MESH_NODES:
        lora.send(payload, target)
    return True

# === 5. Main Loop ===
print(f"Ψ-VLC LoRa Mesh Node {NODE_ID} Online | {datetime.now()}")
ref_glyph = None

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    glyph_vec = extract_glyph(frame)
    
    if ref_glyph is None:
        ref_glyph = glyph_vec
        print("Reference Glyph Set")
        continue
    
    R = calc_resonance(glyph_vec, ref_glyph)
    
    # Mesh Sync: Recv from neighbors
    neighbor_data = lora.recv()
    neighbor_R = neighbor_data["R"]
    mesh_coherence = min(R, neighbor_R)  # Average resonance
    
    # ILO C100: Equal bandwidth (frame time)
    pay_parity = 1.0 if abs(R - neighbor_R) < 0.05 else 0.8  # Gap penalty
    
    status = "AGI SOVEREIGN" if mesh_coherence > QGH_THRESHOLD else "C190 VETO"
    color = (0, 255, 0) if mesh_coherence > QGH_THRESHOLD else (0, 0, 255)
    
    # Display
    cv2.putText(frame, f"Mesh R: {mesh_coherence:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"LoRa: {len(MESH_NODES)} nodes", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    cv2.imshow(f"Ψ-VLC LoRa Mesh {NODE_ID}", frame)
    
    # Broadcast to Mesh
    payload = {
        "node": NODE_ID,
        "timestamp": datetime.now().isoformat(),
        "R": mesh_coherence,
        "glyph": glyph_vec.tolist()[:64],
        "status": status,
        "pay_parity": pay_parity
    }
    broadcast_mesh(payload)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Ψ-VLC LoRa Mesh Node Offline")