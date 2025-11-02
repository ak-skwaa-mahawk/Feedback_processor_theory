# vlc_pi_prototype.py
# Run on Raspberry Pi 5 with Pi Camera
import cv2
import numpy as np
import cupy as cp  # Install via pip (or use numpy if no GPU)
import socket
import time
import json
from datetime import datetime

# === CONFIG ===
NODE_ID = "VLC-PI-001"
CAM_RES = (640, 480)
FPS = 30
GLYPH_SIZE = 16  # 16x16 pixel glyph
QGH_THRESHOLD = 0.997
AMD_HOST = "192.168.1.100"  # AMD mining rig IP
PORT = 5005

# === 1. Initialize Camera ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === 2. Glyph Extraction ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Crop center 16x16
    h, w = gray.shape
    glyph = gray[h//2-8:h//2+8, w//2-8:w//2+8]
    glyph = glyph.astype(np.float32) / 255.0  # Normalize
    return glyph.flatten()

# === 3. Resonance Calculation (QGH Handshake) ===
def calc_resonance(glyph_vec, ref_glyph=None):
    if ref_glyph is None:
        return 1.0
    # Cosine similarity
    dot = np.dot(glyph_vec, ref_glyph)
    norm = np.linalg.norm(glyph_vec) * np.linalg.norm(ref_glyph)
    R = dot / (norm + 1e-8)
    return float(R)

# === 4. Send to AMD Miner ===
def send_to_amd(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((AMD_HOST, PORT))
            s.sendall(json.dumps(data).encode())
        return True
    except:
        return False

# === 5. Main Loop ===
print(f"Ψ-VLC Pi Node {NODE_ID} Online | {datetime.now()}")
ref_glyph = None  # First frame = reference

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    # Extract glyph
    glyph_vec = extract_glyph(frame)
    
    # First frame: set reference
    if ref_glyph is None:
        ref_glyph = glyph_vec
        print("Reference Glyph Set")
        continue
    
    # Compute resonance
    R = calc_resonance(glyph_vec, ref_glyph)
    
    # ILO C100 Check: Equal frame time (pay parity)
    frame_time = 1.0 / FPS
    pay_parity = 1.0  # Assume equal for now
    
    # Status
    status = "AGI SOVEREIGN" if R > QGH_THRESHOLD else "C190 VETO"
    color = (0, 255, 0) if R > QGH_THRESHOLD else (0, 0, 255)
    
    # Display
    cv2.putText(frame, f"R: {R:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow(f"Ψ-VLC {NODE_ID}", frame)
    
    # Send to AMD
    payload = {
        "node": NODE_ID,
        "timestamp": datetime.now().isoformat(),
        "R": R,
        "glyph": glyph_vec.tolist()[:64],  # First 64 values
        "status": status,
        "pay_parity": pay_parity
    }
    if send_to_amd(payload):
        print(f"Sent R={R:.4f} → AMD Miner")
    
    # Exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Ψ-VLC Pi Node Offline")