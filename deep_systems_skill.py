def _get_aosp_internals(self):
        try:
            # Existing battery + cell + eSIM
            bat = json.loads(subprocess.check_output(['termux-battery-status']).decode())
            cell = subprocess.check_output(['termux-telephony-cellinfo']).decode()
            esim_raw = subprocess.check_output(['termux-telephony-esim']).decode() if os.path.exists('/data/data/com.termux/files/usr/bin/termux-telephony-esim') else "{}"
            esim = json.loads(esim_raw) if esim_raw.strip() else {}

            # NEW: Detect Google Fi as carrier
            carrier = subprocess.check_output(['getprop', 'gsm.sim.operator.alpha']).decode().strip()
            is_fi = "fi" in carrier.lower() or "google" in carrier.lower()

            return {
                "battery": bat.get('percentage', 50),
                "temp": bat.get('temperature', 25),
                "phone_rssi": -95 if "signal" not in cell.lower() else -70,
                "esim_profiles": esim.get("profiles", []),
                "esim_enabled": len([p for p in esim.get("profiles", []) if p.get("enabled")]),
                "carrier": carrier,
                "google_fi_active": is_fi,
                "cpu_architecture": platform.machine(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except:
            return {"esim_profiles": [], "esim_enabled": 0, "google_fi_active": False, "battery": 50, "temp": 25, "phone_rssi": -95}