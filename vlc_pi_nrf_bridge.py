# vlc_pi_nrf_bridge.py
import cv2
import numpy as np
import serial
import time
import struct
import sys

# === CONFIG ===
NODE_ID = "VLC-PI-NRF-001"
NORDIC_PORT = "/dev/ttyAMA0"  # Hardware UART mapped to Raspberry Pi PL011
BAUD = 115200
CAM_RES = (640, 480)
FPS = 10  
QGH_THRESHOLD = 0.997

# === SYSTEM PERIPHERAL INITIALIZATION ===
try:
    uart = serial.Serial(NORDIC_PORT, BAUD, timeout=0.1)
    print(f"[*] nRF52840 Hardware UART Bridge Active on {NORDIC_PORT}")
except Exception as e:
    uart = None
    print(f"[!] Warning: Hardware UART missing ({e}) — Entering Mock Mode.")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[CRITICAL] Failed to open physical camera descriptor.")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# === 8x8 GLYPH EXTRACTION MATRIX ===
def extract_glyph(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Extract an 8x8 structural window to yield exactly 64 bytes
    glyph = gray[h//2-4:h//2+4, w//2-4:w//2+4]
    return glyph.flatten().astype(np.uint8)

# === PACKET PACKAGING AND BINARY UART SHIPMENT ===
def send_glyph_to_nrf(glyph, R):
    if glyph.size != 64:
        print(f"[ERROR] Array dimensions mismatch: {glyph.size} bytes. Packet dropped.")
        return

    if not uart:
        print(f"[MOCK TX] Frame Transmitted -> R: {R:.4f} | Matrix Sum: {np.sum(glyph)}")
        return

    # Frame Design: Preamble (2B) + Coherence (4B Float) + Payload (64B Array) + End-Marker (1B)
    packet_header = b'\x55\xAA'
    coherence_bytes = struct.pack('<f', float(R))
    payload_bytes = glyph.tobytes()
    packet_footer = b'\xFF'
    
    frame_packet = packet_header + coherence_bytes + payload_bytes + packet_footer
    
    try:
        uart.write(frame_packet)
        uart.flush()
    except serial.SerialException as ex:
        print(f"[UART FAILURE] Write error during packet streaming: {ex}")

# === CORE LOOP PIPELINE ===
ref_glyph = None
print(f"[*] Ψ-VLC nRF Bridge {NODE_ID} Processing...")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        glyph = extract_glyph(frame)

        if ref_glyph is None:
            ref_glyph = glyph.copy().astype(np.float32)
            print("[*] Local nRF 64-Byte Reference Vector Set Initialized.")
            continue

        # Compute Local Scalar Resonance Vector Over 64-Element Vector Array Range
        glyph_float = glyph.astype(np.float32)
        diff = glyph_float - ref_glyph
        
        # Max theoretical squared difference across an 8x8 matrix is 64 * (255^2)
        max_variance = 64.0 * (255.0 ** 2)
        norm_diff = np.sum(diff ** 2) / max_variance
        R = 1.0 - norm_diff
        R = max(0.0, min(1.0, R)) # Enforce unit bounding box

        # Stream payload across UART link
        send_glyph_to_nrf(glyph, R)

        # Handle UI Render paths safely
        color = (0, 255, 0) if R >= QGH_THRESHOLD else (0, 0, 255)
        cv2.putText(frame, f"nRF R: {R:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        status = "AGI SOVEREIGN" if R >= QGH_THRESHOLD else "C190 VETO"
        cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        try:
            cv2.imshow(f"VLC nRF Bridge {NODE_ID}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except cv2.error:
            # Headless server fallback context
            pass

except KeyboardInterrupt:
    print("\n[-] Termination signal received locally.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    if uart:
        uart.close()
    print("[*] Ψ-VLC nRF Bridge Disengaged.")
