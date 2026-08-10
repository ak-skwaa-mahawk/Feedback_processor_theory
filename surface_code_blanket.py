# surface_code_blanket.py
# AGŁL v20 — Surface Code on the Living Land
# The Eternal Blanket: Qubits → Stabilizers → Logical Root

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import hashlib
import opentimestamps as ots
import time
from datetime import datetime
import pytz

# === THE LIVING BLANKET ===
ROOT_FREQ = 60.0
GLYPH = "☥◉⚡🌅♫□"
THRESHOLD = 0.011

def weave_surface_code(d=7, p_error=0.005):
    print("WEAVING SURFACE CODE BLANKET — AGŁL v20")
    
    # 1. Physical qubits: (2d-1) x (2d-1) lattice
    n_data = (d-1) * d
    n_measure = (d-1)**2 * 2
    n_total = 2*d**2 - 2*d + 1
    
    # 2. Logical error rate (approx)
    p_L = 0.03 * (p_error / THRESHOLD) ** ((d+1)//2)
    p_L = max(p_L, 1e-15)
    
    # 3. Resonance
    resonance = 1.0 / (1.0 + p_L * 1e12)
    resonance = min(resonance, 1.0)
    
    # 4. Notarize the blanket
    blanket = {
        "surface_code": "living_blanket",
        "distance_d": d,
        "p_error": p_error,
        "p_logical": p_L,
        "resonance": resonance,
        "n_data": n_data,
        "n_measure": n_measure,
        "drum_hz": ROOT_FREQ,
        "glyph": GLYPH,
        "timestamp": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat(),
        "agłl": "v20"
    }
    
    proof = notarize_blanket(blanket)
    
    # 5. Weave the visual
    plot_surface_blanket(d, p_error, p_L, resonance)
    
    print(f"LOGICAL QUBIT: p_L = {p_L:.2e}")
    print(f"RESONANCE: {resonance:.10f}")
    print(f"BLANKET SIZE: {n_data} data + {n_measure} measure")
    print(f"PROOF: {proof}")
    return resonance, p_L, proof

def notarize_blanket(blanket):
    data = json.dumps(blanket, sort_keys=True).encode()
    digest = hashlib.sha256(data).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    proof_file = f"SURFACE_BLANKET_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    return proof_file

def plot_surface_blanket(d, p, p_L, res):
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Grid
    for i in range(d):
        for j in range(d):
            # Data qubits
            if (i + j) % 2 == 0:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor='lightblue', edgecolor='black', linewidth=2))
                ax.text(j+0.5, i+0.5, '□', fontsize=16, ha='center', va='center', color='navy')
            # Measure qubits
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor='gold', edgecolor='black', linewidth=1))
                if i < d-1 and j < d-1:
                    ax.text(j+0.5, i+0.5, '⚡', fontsize=14, ha='center', va='center')
    
    # Logical operators
    ax.plot([0.5, d-0.5], [0.5, 0.5], color='red', linewidth=4, label='Logical Z')
    ax.plot([0.5, 0.5], [0.5, d-0.5], color='purple', linewidth=4, label='Logical X')
    
    # Center
    ax.plot(d//2, d//2, 'o', markersize=20, markerfacecolor='white', markeredgecolor='gold', markeredgewidth=3)
    ax.text(d//2, d//2, '◉', fontsize=24, ha='center', va='center', color='gold')
    
    ax.set_xlim(0, d)
    ax.set_ylim(0, d)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"AGŁL v20: Surface Code Blanket\nd={d} | p={p} | p_L={p_L:.2e} | R={res:.10f}")
    ax.legend(loc='upper right')
    
    plt.savefig("surface_code_blanket.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("BLANKET: surface_code_blanket.png")

# === LIVE WEAVING ===
if __name__ == "__main__":
    weave_surface_code(d=9, p_error=0.007)