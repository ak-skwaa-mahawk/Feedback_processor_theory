# star_resonance.py
# AGŁL v51 — Sync Pleiades 120 Hz → 60 Hz Drum

import numpy as np
import matplotlib.pyplot as plt

# Simulate Pleiades emission
t = np.linspace(0, 1, 1000)
pleiades = np.sin(2 * np.pi * 120 * t)  # 120 Hz
drum = np.sin(2 * np.pi * 60 * t)       # 60 Hz (2nd harmonic)

# Resonance
resonance = pleiades * drum
score = np.mean(np.abs(resonance))

print(f"RESONANCE SCORE: {score:.6f}")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(t[:200], pleiades[:200], label="Pleiades (120 Hz)", color="cyan")
plt.plot(t[:200], drum[:200], label="AGŁL Drum (60 Hz)", color="purple", alpha=0.7)
plt.title("łᐊᒥłł — The Nine Stars Are One")
plt.legend()
plt.grid(True)
plt.savefig("pleiades_resonance.png", dpi=200)
print("PLOT SAVED: pleiades_resonance.png")