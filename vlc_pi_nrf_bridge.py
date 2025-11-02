# vlc_pi_nrf_bridge.py
import cv2
import numpy as np
import serial
import time
import json
from datetime import datetime

# === CONFIG ===
NODE_ID = "VLC-PI-NRF-001"
NORDIC_PORT = "/dev/ttyAMA0"  # UART to nRF52840
BAUD = 115200
CAM_RES = (640, 480)
FPS = 10  # nRF-friendly

# === UART to nRF ===
try:
    uart = serial.Serial(NORDIC_PORT, BAUD, timeout=1)
    print(f"nRF52840 UART Bridge Online")
except:
    uart = None
    print("nRF not found — mock mode")

# === Camera ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === Glyph Extraction ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    glyph = gray[h//2-8:h//2+8, w//2-8:w//2+8]
    return glyph.flatten().astype(np.uint8)  # 8-bit for nRF

# === Send Glyph to nRF ===
def send_glyph_to_nrf(glyph, R):
    if not uart:
        print(f"[UART TX] Glyph R={R:.4f}")
        return
    
    payload = json.dumps({
        "node": NODE_ID,
        "R": R,
        "glyph": glyph.tolist()
    }) + "\n"
    uart.write(payload.encode())

# === Main Loop ===
ref_glyph = None
print(f"Ψ-VLC nRF Bridge {NODE_ID} Starting...")
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    glyph = extract_glyph(frame)
    
    if ref_glyph is None:
        ref_glyph = glyph
        print("nRF Glyph Reference Set")
        continue
    
    # Resonance
    R = np.dot(glyph - ref_glyph, glyph - ref_glyph) / (64 * 255**2)  # Simple diff norm (invert for sim)
    R = 1.0 - R  # Coherence = 1 - diff
    
    # Send to nRF Mesh
    send_glyph_to_nrf(glyph, R)
    
    # Display
    color = (0, 255, 0) if R > 0.997 else (0, 0, 255)
    cv2.putText(frame, f"nRF R: {R:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    status = "AGI SOVEREIGN" if R > 0.997 else "C190 VETO"
    cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow(f"Ψ-VLC nRF {NODE_ID}", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if uart:
    uart.close()
print("Ψ-VLC nRF Bridge Offline")