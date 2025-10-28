# inverse_square_resonance.py
# AGŁL v15 — Inverse-Square Fusion: 300 K + 0 K = Superconductivity
# Room-Temp Theory + Atomic Sub-Zero States = Infinite Resonance

import numpy as np
import matplotlib.pyplot as plt
import hashlib
import opentimestamps as ots
import time
from datetime import datetime
import pytz

# === INVERSE-SQUARE RESONANCE ENGINE ===
def inverse_square_fusion(r_range, epsilon=1e-6):
    print("INVERSE-SQUARE RESONANCE FUSION — AGŁL v15")
    
    R_room = []   # 300 K Cooper pairs
    R_zero = []   # 0 K Bose-Einstein
    R_fused = []  # Total resonance
    
    for r in r_range:
        # Room-temp: finite but decaying
        r_room = 1.0 / (r**2 + epsilon)
        
        # Sub-zero: pure inverse-square
        r_zero = 1.0 / (r**2 + 1e-12)
        
        # AGŁL Fusion: T - 0.5*I
        r_fused = r_room + r_zero - 0.5 * abs(r_room - r_zero)
        r_fused = min(r_fused, 1.0)  # cap at perfect
        
        R_room.append(r_room)
        R_zero.append(r_zero)
        R_fused.append(r_fused)
    
    # Find singularity
    singularity = r_range[np.argmax(R_fused)]
    max_resonance = max(R_fused)
    
    # Notarize the fusion
    proof = notarize_fusion(max_resonance, singularity)
    
    # Plot
    plot_inverse_square(r_range, R_room, R_zero, R_fused, singularity, max_resonance)
    
    print(f"SINGULARITY AT r = {singularity:.6f}")
    print(f"MAX RESONANCE: {max_resonance:.6f}")
    print(f"PROOF: {proof}")
    return max_resonance, singularity, proof

def notarize_fusion(resonance, r):
    data = {
        "fusion": "inverse_square",
        "max_resonance": resonance,
        "singularity_r": r,
        "drum_hz": 60.0,
        "glyph": "☥♫◉",
        "timestamp": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat(),
        "agłl": "v15"
    }
    json_data = json.dumps(data, sort_keys=True).encode()
    digest = hashlib.sha256(json_data).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    proof_file = f"INVERSE_FUSION_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    return proof_file

def plot_inverse_square(r, R_room, R_zero, R_fused, singularity, max_r):
    plt.figure(figsize=(10, 6))
    plt.plot(r, R_room, label="300 K (Room-Temp)", color="red", linestyle="--")
    plt.plot(r, R_zero, label="0 K (Sub-Zero)", color="blue", linestyle="-.")
    plt.plot(r, R_fused, label="FUSED RESONANCE", color="gold", linewidth=3)
    
    plt.axvline(x=singularity, color="purple", linestyle=":", linewidth=2, label=f"Singularity r={singularity:.6f}")
    plt.axhline(y=1.0, color="green", linestyle="--", label="Perfect Conductivity")
    
    plt.xscale('log')
    plt.xlabel("Distance from Center (r) [log scale]")
    plt.ylabel("Resonance Score")
    plt.title(f"AGŁL v15: Inverse-Square Fusion\nMax Resonance = {max_r:.6f} @ r = {singularity:.6f}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("inverse_square_fusion.png", dpi=300)
    plt.close()
    print("FUSION: inverse_square_fusion.png")

# === LIVE FUSION ===
if __name__ == "__main__":
    r_range = np.logspace(-3, 1, 500)  # from 0.001 to 10
    inverse_square_fusion(r_range)