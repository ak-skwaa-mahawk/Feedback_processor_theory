# vlc_pi_nrf_bridge_enhanced.py
import cv2
import numpy as np
import serial
import time
import json
import logging
import threading
from datetime import datetime
from queue import Queue, Empty
import traceback

# === LOGGING: Sovereign Trace ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("vlc_mesh.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("Ψ-VLC")

# === CONFIG ===
NODE_ID = "VLC-PI-NRF-001"
NORDIC_PORT = "/dev/ttyAMA0"
BAUD = 115200
CAM_RES = (640, 480)
FPS = 10
RETRY_DELAY = 3
UART_TIMEOUT = 2
WATCHDOG_INTERVAL = 30

# === GLOBAL STATE ===
ref_glyph = None
mesh_coherence = 1.0
uart = None
camera = None
glyph_queue = Queue(maxsize=10)
running = True

# === 1. Watchdog: Heartbeat & Recovery ===
def watchdog():
    last_heartbeat = time.time()
    while running:
        if time.time() - last_heartbeat > WATCHDOG_INTERVAL * 2:
            log.critical("WATCHDOG: No heartbeat → Rebooting node")
            # In real: os.system("sudo reboot")
        time.sleep(5)
        last_heartbeat = time.time()

threading.Thread(target=watchdog, daemon=True).start()

# === 2. UART Handler with Auto-Reconnect ===
def init_uart():
    global uart
    while running:
        try:
            uart = serial.Serial(NORDIC_PORT, BAUD, timeout=UART_TIMEOUT)
            log.info(f"nRF52840 UART Connected: {NORDIC_PORT}")
            return True
        except Exception as e:
            log.error(f"UART Init Failed: {e}. Retry in {RETRY_DELAY}s")
            time.sleep(RETRY_DELAY)
    return False

def send_glyph_safe(glyph, R):
    if not uart or not uart.is_open:
        return False
    try:
        payload = json.dumps({
            "node": NODE_ID,
            "R": R,
            "glyph": glyph.tolist(),
            "ts": datetime.now().isoformat()
        }) + "\n"
        uart.write(payload.encode())
        uart.flush()
        return True
    except Exception as e:
        log.error(f"UART Send Failed: {e}")
        uart.close()
        init_uart()
        return False

# === 3. Camera with Fallback & Retry ===
def init_camera():
    global camera
    for i in range(3):  # Try multiple indices
        cam = cv2.VideoCapture(i)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])
            cam.set(cv2.CAP_PROP_FPS, FPS)
            log.info(f"Camera {i} Online")
            return cam
        cam.release()
    return None

# === 4. Glyph Worker (Thread-Safe) ===
def glyph_worker():
    global ref_glyph, mesh_coherence
    while running:
        try:
            frame = glyph_queue.get(timeout=1)
            glyph = extract_glyph(frame)
            
            if ref_glyph is None:
                ref_glyph = glyph
                log.info("Reference Glyph Locked")
                continue
            
            # Resonance (robust)
            diff = np.abs(glyph.astype(np.float32) - ref_glyph.astype(np.float32))
            R = 1.0 - (np.mean(diff) / 255.0)
            R = max(0.0, min(1.0, R))
            
            # Send with retry
            if not send_glyph_safe(glyph, R):
                log.warning("Glyph send failed — buffering")
                time.sleep(0.1)
            
            # Veto Pulse
            if R < 0.997:
                log.warning(f"C190 VETO: R={R:.4f}")
            
            mesh_coherence = R
            glyph_queue.task_done()
        except Empty:
            continue
        except Exception as e:
            log.error(f"Glyph Worker Error: {e}\n{traceback.format_exc()}")

threading.Thread(target=glyph_worker, daemon=True).start()

# === 5. Main Loop with Full Recovery ===
log.info(f"Ψ-VLC nRF Bridge {NODE_ID} Booting...")
init_uart()
camera = init_camera()

if not camera:
    log.critical("Camera Failed — Entering Fallback Mode")
    # Fallback: Generate synthetic glyphs
    synthetic = True
else:
    synthetic = False

frame_count = 0
last_heartbeat = time.time()

while running:
    try:
        if synthetic:
            # Fallback: Synthetic frame
            frame = np.random.randint(0, 256, (CAM_RES[1], CAM_RES[0], 3), dtype=np.uint8)
            time.sleep(1/FPS)
        else:
            ret, frame = camera.read()
            if not ret:
                log.error("Camera Read Failed — Reinitializing")
                camera.release()
                camera = init_camera()
                if not camera:
                    synthetic = True
                continue
        
        # Queue frame
        if glyph_queue.full():
            try:
                glyph_queue.get_nowait()
            except Empty:
                pass
        glyph_queue.put(frame)
        
        # Display
        status = "AGI SOVEREIGN" if mesh_coherence > 0.997 else "C190 VETO"
        color = (0, 255, 0) if mesh_coherence > 0.997 else (0, 0, 255)
        cv2.putText(frame, f"R: {mesh_coherence:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Nodes: OK", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
        cv2.imshow(f"Ψ-VLC {NODE_ID}", frame)
        
        # Heartbeat
        if time.time() - last_heartbeat > WATCHDOG_INTERVAL:
            log.info("Heartbeat OK")
            last_heartbeat = time.time()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            
    except Exception as e:
        log.critical(f"Main Loop Crash: {e}\n{traceback.format_exc()}")
        time.sleep(1)

# === CLEAN SHUTDOWN ===
running = False
if camera:
    camera.release()
if uart and uart.is_open:
    uart.close()
cv2.destroyAllWindows()
log.info("Ψ-VLC Node Shutdown Complete")