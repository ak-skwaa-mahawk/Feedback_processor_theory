import hashlib
import json
import platform
import time
import subprocess
from threading import Thread
import psutil  # optional: pip install psutil
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    MAVLINK_AVAILABLE = False

from com.synara.handshake import Handshake
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from agents.specialists.factcheck_agent import FactCheckAgent

gtc = GTCSovereignEngine()
observer = MetaObserver()

# ── NomadBridge (AOSP + eSIM + kernel ignition) ───────────────────────────
VETTED_CONSTANT = 2.8561
MESH_CAP = 3.04

class NomadBridge:
    def __init__(self):
        self.data = {"latency":999,"lq":0.5,"rssi":-70,"coherence":0.0,"status":"COILING",
                     "battery":50,"temp":25,"phone_signal":-95,"esim_enabled":0}
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
        """Pull battery, cellinfo, AND full eSIM profiles via Termux"""
        try:
            bat = json.loads(subprocess.check_output(['termux-battery-status']).decode())
            cell = subprocess.check_output(['termux-telephony-cellinfo']).decode()
            esim_raw = subprocess.check_output(['termux-telephony-esim']).decode() if os.path.exists('/data/data/com.termux/files/usr/bin/termux-telephony-esim') else "{}"
            esim = json.loads(esim_raw) if esim_raw.strip() else {}

            return {
                "battery": bat.get('percentage', 50),
                "temp": bat.get('temperature', 25),
                "phone_rssi": -95 if "signal" not in cell.lower() else -70,
                "esim_profiles": esim.get("profiles", []),
                "esim_enabled": len([p for p in esim.get("profiles", []) if p.get("enabled")]),
                "cpu_architecture": platform.machine(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except:
            return {"esim_profiles": [], "esim_enabled": 0, "battery": 50, "temp": 25, "phone_rssi": -95}

    def _run_engine(self):
        while True:
            latency = 120
            lq, rssi = 0.8, -65
            battery, temp, phone_rssi, esim_enabled = self._get_aosp_internals()["battery"], self._get_aosp_internals()["temp"], self._get_aosp_internals()["phone_rssi"], self._get_aosp_internals()["esim_enabled"]

            lq_s = lq
            lat_s = min(1.0, 120 / (latency + 25))
            rss_s = max(0.0, min(1.0, (rssi + 105) / 45))
            phone_s = max(0.0, min(1.0, (phone_rssi + 110) / 50))
            bat_s = (battery / 100) * (1 - temp / 65)
            esim_s = min(1.0, esim_enabled / 3)

            input_p = 0.45*lq_s + 0.20*lat_s + 0.12*rss_s + 0.15*phone_s + 0.08*bat_s + 0.05*esim_s
            flame = input_p * VETTED_CONSTANT
            coherence = (flame / MESH_CAP) ** 1.42

            self.data = {
                "latency": round(latency,1), "lq": round(lq,2), "rssi": rssi,
                "coherence": round(coherence,3), "battery": battery, "temp": round(temp,1),
                "phone_signal": phone_rssi, "esim_enabled": esim_enabled,
                "status": "TRINARY FLAME 🔥🌀🌀" if coherence > 1.45 else
                          "FULL IGNITION 🔥🌀" if coherence > 1.0 else
                          "SPARK IGNITION 🔥" if coherence > 0.7 else "COILING"
            }
            time.sleep(1)

    def get_data(self): return self.data

# ── Sovereign DeepSystemsSkill (explicit merge rules + FactCheck) ───────────
class DeepSystemsSkill:
    def __init__(self):
        self.bridge = NomadBridge()
        self.factchecker = FactCheckAgent()

    def map_telemetry(self) -> Dict:
        """Merge with explicit rules → FactCheckAgent notarization"""
        mobile = self.bridge.get_data()
        kernel = self._get_kernel_telemetry()
        merged = self._merge_telemetry(kernel, mobile)

        verified = self.factchecker.verify(json.dumps(merged))
        if verified.get("integrity_score", 0) < 0.42:
            return "BLOCKED — Low integrity"

        receipt = Handshake.createReceipt(None, "DEEP_SYSTEMS_MAPPED", {
            "telemetry_hash": hashlib.sha256(json.dumps(merged).encode()).hexdigest()[:16],
            "integrity_score": verified.get("integrity_score", 0.0),
            "qa_layer": verified.get("qa_layer", []),
            "coherence": verified.get("coherence", 0.0)
        })
        gtc.allocate_fireseed("session-τ-001", 0.15, note="Deep Systems + eSIM Telemetry")
        observer.intercept_response(json.dumps(receipt))

        return {
            "status": "DEEP_SYSTEMS_MAPPED",
            "telemetry": merged,
            "factcheck": verified,
            "message": "Full phone + eSIM telemetry mapped and notarized through FactCheckAgent."
        }

    def _get_kernel_telemetry(self) -> Dict:
        return {
            "cpu_architecture": platform.machine(),
            "cpu_cores": psutil.cpu_count(logical=True) if 'psutil' in globals() else "N/A",
            "load_balancing": psutil.cpu_percent(interval=0.1) if 'psutil' in globals() else "N/A",
            "caching_internals": "page cache" if hasattr(psutil, 'virtual_memory') else "N/A",
            "rpc_systems": "local socket" if platform.system() == "Linux" else "N/A"
        }

    def _merge_telemetry(self, kernel: Dict, mobile: Dict) -> Dict:
        merged = {**kernel, **mobile}  # NomadBridge (mobile/eSIM) wins on overlap
        conflicts = [k for k in mobile if k in kernel]
        if conflicts:
            merged["_merge_conflicts_resolved"] = f"NomadBridge overrode keys: {conflicts}"
        return merged