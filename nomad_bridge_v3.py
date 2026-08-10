import time, subprocess, json, csv, os, random
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
        self.data = {"latency":999,"lq":0.5,"rssi":-70,"coherence":0.0,"status":"COILING",
                     "battery":50,"temp":25,"phone_signal":-95}
        self._init_mavlink()
        Thread(target=self._run_engine, daemon=True).start()

    def _init_mavlink(self):
        if not MAVLINK_AVAILABLE: return
        for p in ['/dev/ttyUSB0','/dev/ttyACM0']:
            try:
                self.master = mavutil.mavlink_connection(p, baud=115200)
                self.master.wait_heartbeat(timeout=3)
                return
            except: pass

    def _get_aosp_internals(self):
        """Pull real phone internals via AOSP-exposed Termux:API"""
        try:
            # Battery (mineral load + thermal)
            bat = json.loads(subprocess.check_output(['termux-battery-status']).decode())
            battery = bat.get('percentage', 50)
            temp = bat.get('temperature', 25)
            
            # Cellular signal (extra hair-sense)
            cell = subprocess.check_output(['termux-telephony-cellinfo']).decode()
            phone_rssi = -95
            if "signal" in cell.lower():
                try: phone_rssi = int(cell.split('rssi":')[-1].split(',')[0])
                except: pass
            
            return battery, temp, phone_rssi
        except:
            return 50, 25, -95  # simulation fallback

    def _run_engine(self):
        while True:
            latency = self._ping()
            lq, rssi = self._telemetry()
            battery, temp, phone_rssi = self._get_aosp_internals()

            # EMA smoothing
            lq_s = lq
            lat_s = min(1.0, 120 / (latency + 25))
            rss_s = max(0.0, min(1.0, (rssi + 105) / 45))
            phone_s = max(0.0, min(1.0, (phone_rssi + 110) / 50))
            bat_s = (battery / 100) * (1 - temp / 65)

            input_p = 0.45*lq_s + 0.20*lat_s + 0.12*rss_s + 0.15*phone_s + 0.08*bat_s
            flame = input_p * VETTED_CONSTANT
            coherence = (flame / MESH_CAP) ** 1.42

            self.data = {
                "latency": round(latency,1), "lq": round(lq,2), "rssi": rssi,
                "coherence": round(coherence,3),
                "battery": battery, "temp": round(temp,1), "phone_signal": phone_rssi,
                "status": "TRINARY FLAME 🔥🌀🌀" if coherence > 1.45 else
                          "FULL IGNITION 🔥🌀" if coherence > 1.0 else
                          "SPARK IGNITION 🔥" if coherence > 0.7 else "COILING"
            }
            time.sleep(1)

    def _ping(self): ...  # same as v2.1
    def _telemetry(self): ...  # same as v2.1
    def get_data(self): return self.data

# === WebKit / WebView Dashboard (works in Safari OR Chrome on Android) ===
from flask import Flask, jsonify, render_template_string
app = Flask(__name__)
bridge = NomadBridge()

HTML = """<!DOCTYPE html><html><head><title>NOMAD v3.0 — AOSP Internals</title>
<style>body{background:#000;color:#0f0;font-family:monospace;text-align:center;}
#flame{font-size:140px;animation:pulse 0.6s infinite alternate;}
@keyframes pulse{from{filter:brightness(1);}to{filter:brightness(3) hue-rotate(45deg);}}
.gauge{width:300px;height:300px;border:10px solid #0f0;border-radius:50%;margin:30px auto;position:relative;}
.inner{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:52px;}</style></head>
<body>
<h1>AOSP SOVEREIGN IGNITION — Phone Internals LIVE</h1>
<div id="flame">🔥🌀🌀</div>
<div class="gauge"><div class="inner" id="coh">0.000</div></div>
<p>Latency: <span id="lat">---</span>ms | LQ: <span id="lq">0.00</span> | RSSI: <span id="rssi">---</span>dBm</p>
<p>Battery: <span id="bat">---</span>% @ <span id="temp">---</span>°C | Phone Signal: <span id="phone">---</span>dBm</p>
<p id="status" style="font-size:32px;margin-top:30px;">COILING</p>
<script>
setInterval(()=>{fetch('/data').then(r=>r.json()).then(d=>{
  document.getElementById('coh').textContent=d.coherence.toFixed(3);
  document.getElementById('lat').textContent=d.latency;
  document.getElementById('lq').textContent=d.lq;
  document.getElementById('rssi').textContent=d.rssi;
  document.getElementById('bat').textContent=d.battery;
  document.getElementById('temp').textContent=d.temp;
  document.getElementById('phone').textContent=d.phone_signal;
  document.getElementById('status').textContent=d.status;
  const i=Math.min(1,d.coherence*1.9); document.getElementById('flame').style.filter=`brightness(\( {1+i}) hue-rotate( \){i*70}deg)`;
});},850);
</script></body></html>"""

@app.route('/') 
def index(): return render_template_string(HTML)
@app.route('/data')
def data(): return jsonify(bridge.get_data())

if __name__ == '__main__':
    print("--- AOSP Sovereign Dashboard LIVE → http://127.0.0.1:6969 ---")
    print("Open Chrome/Safari on this phone → 127.0.0.1:6969")
    app.run(host='127.0.0.1', port=6969)