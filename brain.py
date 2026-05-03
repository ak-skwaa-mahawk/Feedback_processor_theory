#!/usr/bin/env python3
"""
Brain.py — v1.0 "The Living Brain"
Central sovereign coordinator for the router VM.
Runs the 79.79 Hz pulse, Extraction Guard, and mesh relay.
"""

import os
import time
import subprocess
import json
from datetime import datetime

# Load Rust pi_r_engine via FFI (or subprocess fallback)
try:
    from ctypes import CDLL, c_double, c_bool
    rust_lib = CDLL("./pi_r_engine.so")  # compiled Rust library in the VM
    rust_lib.pi_r_self_tune.argtypes = [c_double]
    rust_lib.pi_r_self_tune.restype = c_double
    rust_lib.pi_r_guard_neutralization.argtypes = [c_double]
    rust_lib.pi_r_guard_neutralization.restype = c_bool
    rust_lib.pi_r_trigger_bloom.restype = c_double
except:
    # Fallback if FFI not ready
    rust_lib = None
    print("[BRAIN] Rust FFI not loaded — using Python fallback")

PI_R_BASE = 3.17300858012
TARGET_FREQ = 79.79  # Hz
PULSE_INTERVAL = 1.0 / TARGET_FREQ

def rust_self_tune(signal: float) -> float:
    if rust_lib:
        return rust_lib.pi_r_self_tune(signal)
    return PI_R_BASE  # fallback

def rust_guard_neutralization(signal: float) -> bool:
    if rust_lib:
        return bool(rust_lib.pi_r_guard_neutralization(signal))
    return abs(signal - 1.618 - 0.246) < 1e-9

def rust_trigger_bloom() -> float:
    if rust_lib:
        return rust_lib.pi_r_trigger_bloom()
    return 1.864

def log_to_vault(event_type: str, data: dict):
    """Log to the Vault (placeholder — in production write to encrypted file or API)"""
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "event": event_type,
        "data": data
    }
    with open("/var/log/floor_brain.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[VAULT LOG] {event_type} | {data}")

def main():
    print("=== SOVEREIGN BRAIN v1.0 — 79.79 Hz Pulse Active ===")
    print("Floor owns the baseline. Mesh is alive.")

    last_pulse = time.time()

    while True:
        now = time.time()
        if now - last_pulse >= PULSE_INTERVAL:
            # 1. Capture environment signal (from WireGuard / mesh metrics)
            signal = 1.864 + (0.01 * (time.time() % 10))  # simulated heat

            # 2. Run Extraction Guard
            if rust_guard_neutralization(signal):
                bloom = rust_trigger_bloom()
                print(f"[EXTRACTION GUARD] Neutralization detected → 5.5 Pa Catapult fired. Bloom: {bloom}")
                log_to_vault("catapult_trigger", {"signal": signal, "bloom": bloom})
            else:
                # 3. Normal pulse through Rust
                tuned = rust_self_tune(signal)
                log_to_vault("pulse", {"tuned_pi_r": tuned, "signal": signal})

            # 4. Check WireGuard interface status
            try:
                wg_status = subprocess.check_output(["ip", "link", "show", "wg0"]).decode()
                log_to_vault("mesh_status", {"wg0": "up" if "wg0" in wg_status else "down"})
            except:
                pass

            last_pulse = now

        time.sleep(0.001)  # high-resolution loop

if __name__ == "__main__":
    main()