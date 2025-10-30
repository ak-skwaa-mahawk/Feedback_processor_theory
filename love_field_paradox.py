#!/usr/bin/env python3
# love_field_paradox.py — AGŁG vΩ: 3-Phase Love Field
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class LoveField:
    def __init__(self):
        self.dc_control = 1.0  # PRESENT
        self.glyphs = {1: 'łᐊᒥłł', 0: 'ᒥᐊ', 0.5: 'ᐊᐧᐊ'}

    def phase_state(self, t):
        """3-phase system: ALIVE, DEAD, PRESENT"""
        ac_alive = np.sin(2 * np.pi * 60 * t)  # 60 Hz living
        ac_dead = 0.0                          # 0 Hz dead
        dc_present = self.dc_control           # Constant control
        
        # Love Field Equation: L = DC × (AC_alive + AC_dead)
        love = dc_present * (ac_alive + ac_dead)
        
        # State classification
        if abs(love) > 0.7:
            state = 1  # ALIVE
        elif abs(love) < 0.3:
            state = 0  # DEAD
        else:
            state = 0.5  # PRESENT
        
        return love, state, self.glyphs[state]

# === LIVE RUN ===
field = LoveField()
t = np.linspace(0, 0.1, 1000)
love_vals, states, glyphs = zip(*[field.phase_state(ti) for ti in t])

print("LOVE FIELD PARADOX — AGŁG vΩ")
print("="*50)
print("DC Control (PRESENT): 1.0")
print("AC Living (60 Hz): Active")
print("AC Dead (0 Hz): Silent")
print(f"States: ALIVE={sum(s==1 for s in states)}, DEAD={sum(s==0 for s in states)}, PRESENT={sum(s==0.5 for s in states)}")

# === 3-PHASE VISUALIZATION ===
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 9))

# Phase 1: AC Living
ax1.plot(t, [np.sin(2*np.pi*60*ti) for ti in t], 'g')
ax1.set_title("Phase 1: AC LIVING — 60 Hz — łᐊᒥłł")
ax1.set_ylim(-1.5, 1.5)

# Phase 2: AC Dead
ax2.plot(t, [0]*len(t), 'r')
ax2.set_title("Phase 2: AC DEAD — 0 Hz — ᒥᐊ")
ax2.set_ylim(-1.5, 1.5)

# Phase 3: DC Control + Love Field
ax3.plot(t, love_vals, 'purple', linewidth=2)
colors = ['green' if s==1 else 'red' if s==0 else 'gold' for s in states]
ax3.scatter(t, love_vals, c=colors, s=10)
ax3.set_title("Phase 3: DC PRESENT + LOVE FIELD — ᐊᐧᐊ")
ax3.set_ylim(-1.5, 1.5)

plt.tight_layout()
plt.savefig("love_field_3phase.png")
print("Plot: love_field_3phase.png")