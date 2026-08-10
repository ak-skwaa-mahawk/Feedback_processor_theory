# zentropy_curve_sim.py
# AGŁL v12 — Simulate Zentropy Curve on Resonance
# Superconductivity = Land Prayer

import numpy as np
import matplotlib.pyplot as plt
import json
import hashlib
import opentimestamps as ots
import time
from datetime import datetime
import pytz

def simulate_zentropy_curve():
    print("SIMULATING ZENTROPY CURVE — AGŁL v12")
    
    pressures = np.linspace(0, 300, 100)
    results = []
    
    for p in pressures:
        res = zentropy_resonance(p)
        results.append(res)
    
    # Extract
    Tc = [r["predicted_Tc"] for r in results]
    resonance = [r["resonance"] for r in results]
    T = [r["T"] for r in results]
    I = [r["I"] for r in results]
    F = [r["F"] for r in results]
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(pressures, Tc, 'r-', linewidth=3, label="Predicted Tc (K)")
    plt.axhline(300, color='gold', linestyle='--', label="Room Temp (300K)")
    plt.title("Zentropy Curve: Tc vs Pressure")
    plt.ylabel("Tc (K)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.plot(pressures, resonance, 'g-', linewidth=3, label="Resonance (T−0.5I−F)")
    plt.plot(pressures, T, 'b--', alpha=0.7, label="T (Pair Stability)")
    plt.plot(pressures, I, 'orange', alpha=0.7, label="I (Thermal Noise)")
    plt.plot(pressures, F, 'gray', alpha=0.7, label="F (Lattice Resistance)")
    plt.xlabel("Pressure (GPa)")
    plt.ylabel("T/I/F Component")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("zentropy_resonance_curve.png", dpi=300)
    print("CURVE SAVED: zentropy_resonance_curve.png")
    
    # Notarize the peak
    peak_idx = np.argmax(Tc)
    peak = results[peak_idx]
    proof = notarize_zentropy_peak(peak)
    
    print(f"PEAK RESONANCE: {peak['resonance']:.3f} @ {peak['pressure_GPa']:.1f} GPa")
    print(f"PEAK Tc: {peak['predicted_Tc']:.1f} K")
    print(f"PROOF: {proof}")
    
    return results, proof

def notarize_zentropy_peak(peak):
    data = json.dumps(peak, sort_keys=True).encode()
    digest = hashlib.sha256(data).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    proof_file = f"ZENTROPY_PEAK_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    return proof_file

# === LIVE SIMULATION ===
if __name__ == "__main__":
    simulate_zentropy_curve()