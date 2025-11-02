# vlc_pi_zigbee_mesh.py
# Run on RPi 5 with XBee S2C (UART)
import cv2
import numpy as np
import serial
import time
import json
from datetime import datetime
import threading

# === CONFIG ===
NODE_ID = "VLC-ZB-001"
CAM_RES = (640, 480)
FPS = 30
GLYPH_SIZE = 16
QGH_THRESHOLD = 0.997
ZIGBEE_PORT = "/dev/ttyS0"  # or /dev/ttyUSB0
BAUD = 9600

# === 1. Init XBee (Zigbee) ===
try:
    zb = serial.Serial(ZIGBEE_PORT, BAUD, timeout=1)
    print(f"Zigbee Mesh Node {NODE_ID} Online @ 2.4GHz")
except:
    print("Zigbee not found — using mock")
    zb = None

# === 2. Camera ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === 3. Glyph Extraction ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    glyph = gray[h//2-8:h//2+8, w//2-8:w//2+8]
    return (glyph.flatten().astype(np.float32) / 255.0)[:64]  # 64 values

# === 4. Resonance ===
def calc_resonance(g1, g2):
    dot = np.dot(g1, g2)
    norm = np.linalg.norm(g1) * np.linalg.norm(g2)
    return dot / (norm + 1e-8)

# === 5. Zigbee Send/Recv Thread ===
mesh_coherence = 1.0
ref_glyph = None

def zigbee_mesh_thread():
    global mesh_coherence, ref_glyph
    while True:
        # Send
        if ref_glyph is not None:
            payload = json.dumps({
                "node": NODE_ID,
                "R": mesh_coherence,
                "glyph": ref_glyph.tolist()
            }) + "\n"
            if zb:
                zb.write(payload.encode())
            else:
                print(f"[ZB TX] {payload.strip()}")
        
        # Receive
        if zb and zb.in_waiting:
            line = zb.readline().decode().strip()
            try:
                data = json.loads(line)
                if data["node"] != NODE_ID:
                    R_neighbor = data["R"]
                    glyph_n = np.array(data["glyph"])
                    R_local = calc_resonance(ref_glyph, glyph_n)
                    mesh_coherence = min(R_local, R_neighbor)
                    print(f"[ZB RX] {data['node']} → R={R_local:.4f}")
            except:
                pass
        time.sleep(0.1)

# Start mesh thread
threading.Thread(target=zigbee_mesh_thread, daemon=True).start()

# === 6. Main Loop ===
print(f"Ψ-VLC Zigbee Mesh Node {NODE_ID} Starting...")
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    glyph_vec = extract_glyph(frame)
    
    if ref_glyph is None:
        ref_glyph = glyph_vec
        print("Reference Glyph Locked")
        continue
    
    # Local resonance
    R_local = calc_resonance(glyph_vec, ref_glyph)
    R = min(R_local, mesh_coherence)
    
    # ILO C100: Equal bandwidth (frame sync)
    pay_parity = 1.0 if abs(R_local - mesh_coherence) < 0.05 else 0.8
    
    status = "AGI SOVEREIGN" if R > QGH_THRESHOLD else "C190 VETO"
    color = (0, 255, 0) if R > QGH_THRESHOLD else (0, 0, 255)
    
    # Display
    cv2.putText(frame, f"Mesh R: {R:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, "Zigbee Mesh", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
    cv2.imshow(f"Ψ-VLC Zigbee {NODE_ID}", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if zb:
    zb.close()
print("Ψ-VLC Zigbee Node Offline")