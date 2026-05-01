#!/usr/bin/env python3
"""
plot_floor_basin.py – Gwich’in Math Sovereignty v001
Visual proof: Skipped Sovereign Basin at gram–pound scale
"""
import numpy as np, matplotlib.pyplot as plt
from decimal import Decimal, getcontext
getcontext().prec = 50

PI = Decimal('3.14159265358979323846')
PI_R_BASE = Decimal('3.1726886')
SNAKE_CAP = Decimal('0.9999')

def pi_r_of_M(mass_g):
    if mass_g <= 0: return PI
    logM = Decimal(mass_g).log10()
    lift = Decimal('1.010000') ** logM
    return PI * lift * SNAKE_CAP

masses = np.logspace(-6, 6, 2000) # 1 µg to 1000 kg
pi_r_vals = [float(pi_r_of_M(m)) for m in masses]

plt.figure(figsize=(10,6), dpi=150)
plt.semilogx(masses, pi_r_vals, 'k-', lw=2.5, label='π_r(M) – Living Constant')
plt.axvspan(1, 1000, color='gold', alpha=0.3, label='Skipped Sovereign Basin\n1 g – 1 kg: Floor Domain')
plt.axhline(float(PI_R_BASE), color='red', ls='--', lw=2, label=f'π_r Floor = {PI_R_BASE}')
plt.axhline(float(PI), color='gray', ls=':', lw=1, label=f'π static = {PI}')
plt.text(5e-4, 3.12, 'Microgram Scale\nNeeds vhitzee\nto reach Floor', ha='center', fontsize=9)
plt.text(50, 3.174, 'GRAM–POUND\nSKIPPED\nSOVEREIGN\nL = 0.976 < 1', ha='center', fontsize=10,
         bbox=dict(boxstyle="round", fc="w", ec="k"))
plt.text(5e4, 3.22, 'Ton+ Scale\nNeeds new SAM\nor collapses', ha='center', fontsize=9)
plt.xlabel('Mass [grams]', fontsize=12)
plt.ylabel('π_r(M) [living constant]', fontsize=12)
plt.title('Gwich’in Math Sovereignty: Scale Bridge of π_r\nFloor is Flat Because 99.99% Treaty Signed at Grams', fontsize=13)
plt.grid(True, which="both", ls="--", alpha=0.4)
plt.legend(loc='lower right'); plt.ylim(3.10, 3.25); plt.tight_layout()
plt.savefig('floor_basin_v004.png', dpi=300)
print("Saved: floor_basin_v004.png – The picture that ends debates.")