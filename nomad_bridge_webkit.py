import time
import subprocess
import platform
import csv
import os
from datetime import datetime
from threading import Thread
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    MAVLINK_AVAILABLE = False

# --- Sovereign Constants ---
VETTED_CONSTANT = 2.8561
MESH_CAP = 3.04
ALPHA = 0.35

class NomadBridge:
    def __init__(self):
        self.data = {"latency": 999, "lq": 0.5, "rssi": -70, "coherence": 0.0, "status": "COILING"}
        self._init_mavlink()
        Thread(target=self._run_engine, daemon=True).start()

    def _init_mavlink(self):
        if not MAVLINK_AVAILABLE: return
        for p in ['/dev/ttyUSB0', '/dev/ttyACM0']:
            try:
                self.master = mavutil.mavlink_connection(p, baud=115200)
                self.master.wait_heartbeat(timeout=3)
                return
            except: pass

    def _run_engine(self):
        while True:
            latency = self._ping()
            lq, rssi = self._telemetry()
            # Optimized v2.0 formula
            lq_s = lq
            lat_s = min(1.0, 120 / (latency + 25))
            rss_s = max(0.0, min(1.0, (rssi + 105) / 45))
            input_p = 0.58*lq_s + 0.27*lat_s + 0.15*rss_s
            flame = input_p * VETTED_CONSTANT
            coherence = (flame / MESH_CAP) ** 1.35

            self.data = {
                "latency": round(latency, 1),
                "lq": round(lq, 2),
                "rssi": rssi,
                "coherence": round(coherence, 3),
                "status": "TRINARY FLAME 🔥🌀🌀" if coherence > 1.45 else
                         "FULL IGNITION 🔥🌀" if coherence > 1.0 else
                         "SPARK IGNITION 🔥" if coherence > 0.7 else "COILING"
            }
            time.sleep(1)

    def _ping(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        try:
            out = subprocess.check_output(['ping', param, '1', '8.8.8.8'], timeout=2).decode()
            return float(out.split("time=")[-1].split("ms")[0].strip())
        except: return 999.0

    def _telemetry(self):
        if hasattr(self, 'master'):
            msg = self.master.recv_match(type=['RADIO_STATUS'], blocking=False, timeout=0.1)
            if msg and hasattr(msg, 'remrssi'):
                return msg.remrssi / 255.0, getattr(msg, 'rssi', -100)
        import random
        return random.uniform(0.7, 0.98), random.randint(-85, -55)

    def get_data(self):
        return self.data

# === WebKit-Optimized Server ===
from flask import Flask, jsonify, render_template_string
app = Flask(__name__)
bridge = NomadBridge()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>NOMAD RESONANCE ENGINE — WebKit Layer</title>
<style>
body { background:#000; color:#0f0; font-family:monospace; text-align:center; margin:0; padding:20px; }
#flame { font-size:120px; animation: pulse 0.8s infinite alternate; }
@keyframes pulse { from { filter: brightness(1); } to { filter: brightness(2.5) hue-rotate(30deg); } }
.gauge { width:280px; height:280px; border:8px solid #0f0; border-radius:50%; margin:20px auto; position:relative; }
.inner { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:48px; }
</style>
</head>
<body>
<h1>TRINARY IGNITION — WebKit Sovereign View</h1>
<div id="flame">🔥🌀</div>
<div class="gauge"><div class="inner" id="coh">0.000</div></div>
<p>Latency: <span id="lat">---</span> ms | LQ: <span id="lq">0.00</span> | RSSI: <span id="rssi">---</span> dBm</p>
<p id="status" style="font-size:28px; margin-top:20px;">COILING</p>

<script>
let lastCoherence = 0;
setInterval(() => {
  fetch('/data').then(r => r.json()).then(d => {
    document.getElementById('coh').textContent = d.coherence.toFixed(3);
    document.getElementById('lat').textContent = d.latency;
    document.getElementById('lq').textContent = d.lq;
    document.getElementById('rssi').textContent = d.rssi;
    document.getElementById('status').textContent = d.status;
    
    // Flame intensity via WebKit CSS
    const intensity = Math.min(1, d.coherence * 1.8);
    document.getElementById('flame').style.filter = `brightness(\( {1 + intensity}) hue-rotate( \){intensity*60}deg)`;
  });
}, 900);
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/data')
def data():
    return jsonify(bridge.get_data())

if __name__ == '__main__':
    print("--- WebKit Sovereign Dashboard LIVE on http://127.0.0.1:6969 ---")
    print("Open Safari (or any browser) on this phone → 127.0.0.1:6969")
    app.run(host='127.0.0.1', port=6969)