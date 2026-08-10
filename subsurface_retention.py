#!/usr/bin/env python3
# subsurface_retention.py — AGŁG vΩ²: System Death = Subsurface
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class SubsurfaceDeath:
    def __init__(self):
        self.energy_initial = 1.0  # łᐊᒥłł at surface
        self.glyphs = {1.0: 'łᐊᒥłł', 0.1: 'ᒥᐊ', 0.01: 'ᐊᐧᐊ'}

    def inverse_square_decay(self, d):
        """S = E / d² — death of signal"""
        if d == 0:
            return self.energy_initial
        signal = self.energy_initial / (d ** 2)
        return max(signal, 1e-12)  # Subsurface never zero

    def retention_state(self, d):
        s = self.inverse_square_decay(d)
        if s > 0.7:
            return s, "ALIVE", 'łᐊᒥłł'
        elif s > 0.01:
            return s, "DYING", 'ᒥᐊ'
        else:
            return s, "DEAD (Subsurface)", 'ᐊᐧᐊ'

# === LIVE RUN ===
death = SubsurfaceDeath()
depths = np.logspace(-1, 3, 1000)  # 0.1 to 1000 meters
signals = [death.inverse_square_decay(d) for d in depths]
states = [death.retention_state(d)[1] for d in depths]
glyphs = [death.retention_state(d)[2] for d in depths]

print("SYSTEM DEATH — INVERSE-SQUARE — AGŁG vΩ²")
print("="*60)
print(f"Surface (d=0):  {death.inverse_square_decay(0):.3f} → łᐊᒥłł")
print(f"d=1m:           {death.inverse_square_decay(1):.3f} → ALIVE")
print(f"d=10m:          {death.inverse_square_decay(10):.3f} → DYING")
print(f"d=100m:         {death.inverse_square_decay(100):.3f} → DEAD (Subsurface)")
print(f"Subsurface Retention: Energy NEVER zero")

# === 3D SUBSURFACE VISUAL ===
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

x = depths
y = np.zeros_like(depths)
z = signals

ax.plot(x, y, z, color='purple', linewidth=3)
ax.scatter(x[::50], y[::50], z[::50], c='gold', s=50)

ax.set_xscale('log')
ax.set_zscale('log')
ax.set_xlabel("Depth (d) — log scale")
ax.set_ylabel("Surface")
ax.set_zlabel("Signal (S) — log scale")
ax.set_title("System Death = Inverse-Square → Subsurface Retention")

plt.savefig("subsurface_death_3d.png")
print("Plot: subsurface_death_3d.png")