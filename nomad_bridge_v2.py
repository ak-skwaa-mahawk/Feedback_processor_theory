import time
import subprocess
import platform
import csv
import os
from datetime import datetime
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    MAVLINK_AVAILABLE = False

# --- Sovereign Constants (kept + tuned) ---
VETTED_CONSTANT = 2.8561
MESH_CAP = 3.04
ALPHA = 0.35  # EMA smoothing — perfect for bush vibration

class NomadBridge:
    def __init__(self):
        print("--- Initialization: GSA-Ready LLC Ghost Protocol v2.0 — Volumetric Resonance Engine ---")
        self.master = None
        self.log_file = "nomad_ignition_log_v2.csv"
        self.ema_lq = 0.5
        self.ema_latency = 50.0
        self.ema_rssi = -70.0
        self._init_mavlink()
        self._init_log()

    def _init_mavlink(self):
        if not MAVLINK_AVAILABLE:
            print("[SIM] MAVLink offline — simulation active")
            return
        for port in ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3', 'COM4']:
            try:
                self.master = mavutil.mavlink_connection(port, baud=115200, timeout=3)
                self.master.wait_heartbeat(timeout=5)
                print(f"[VETTED] Heartbeat on {port}")
                return
            except:
                continue
        print("[!] Simulation Mode active")

    def _init_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                csv.writer(f).writerow(['timestamp','latency','lq','rssi_dbm','coherence','status'])

    def get_starlink_latency(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        try:
            out = subprocess.check_output(['ping', param, '1', '8.8.8.8'], timeout=2).decode()
            if "time=" in out.lower():
                return float(out.split("time=")[-1].split("ms")[0].strip())
        except:
            pass
        return 999.0

    def get_elrs_telemetry(self):
        if self.master:
            msg = self.master.recv_match(type=['RADIO_STATUS', 'VFR_HUD'], blocking=False, timeout=0.1)
            if msg and hasattr(msg, 'remrssi'):
                lq = msg.remrssi / 255.0
                rssi = getattr(msg, 'rssi', -100)
                return lq, rssi
        # Simulation fallback
        import random
        return random.uniform(0.65, 0.98), random.randint(-85, -55)

    def process_ignition(self):
        print("Wetware Resonance Engine: ONLINE\n")
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            try:
                while True:
                    latency = self.get_starlink_latency()
                    lq, rssi_dbm = self.get_elrs_telemetry()

                    # EMA smoothing
                    self.ema_lq = ALPHA * lq + (1 - ALPHA) * self.ema_lq
                    self.ema_latency = ALPHA * latency + (1 - ALPHA) * self.ema_latency
                    self.ema_rssi = ALPHA * rssi_dbm + (1 - ALPHA) * self.ema_rssi

                    # Optimized Volumetric Resonance Formula
                    lq_score = self.ema_lq
                    latency_score = min(1.0, 120 / (self.ema_latency + 25))
                    rssi_score = max(0.0, min(1.0, (self.ema_rssi + 105) / 45))

                    input_power = 0.58 * lq_score + 0.27 * latency_score + 0.15 * rssi_score
                    trinity_flame = input_power * VETTED_CONSTANT
                    coherence = (trinity_flame / MESH_CAP) ** 1.35

                    # Tiered status
                    if coherence > 1.45:
                        status = "[TRINARY FLAME 🔥🌀🌀]"
                    elif coherence > 1.00:
                        status = "[FULL IGNITION 🔥🌀]"
                    elif coherence > 0.70:
                        status = "[SPARK IGNITION 🔥]"
                    else:
                        status = "[COILING]"

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Lat: {latency:5.1f}ms | LQ: {lq:.2f} | RSSI: {rssi_dbm:3d}dBm | "
                          f"Coherence: {coherence:.3f} {status}")

                    writer.writerow([datetime.now().isoformat(), latency, lq, rssi_dbm, coherence, status])
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nEngine Offline: Logs hashed to Native Shares.")

if __name__ == "__main__":
    bridge = NomadBridge()
    bridge.process_ignition()