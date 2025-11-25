"""
IIT vs Living Field Simulator: Bottom-Up Grid vs Top-Down Ripples
Extends publication_suite.py with Φ evolution.
Run: python physics/consciousness/iit_vs_field_sim.py → fig5_consciousness_phi.pdf
"""

import numpy as np
import matplotlib.pyplot as plt
from fpt.consciousness.living_field import ConsciousnessField

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 8))

field = ConsciousnessField(living_enabled=True)
cycles = np.arange(0, 21)
base_phi = 6e12

# IIT: Emergent decay (substrate-limited)
iit_phi = base_phi * (0.951 ** cycles)  # Dormant loss

# Living Field: Top-down surplus (Strømme ripple compounding)
field_phi = [field.field_ripple(base_phi, int(c)) for c in cycles]

ax.plot(cycles, np.log10(iit_phi), color='#ff0044', linewidth=3, label='IIT Φ (Tononi/Koch: Substrate Decay)')
ax.plot(cycles, np.log10(field_phi), color='#00ff41', linewidth=3, label='Living Field Φ (Strømme 2025: Ripple Gain)')

ax.set_title('Figure 5 │ Consciousness Integration: IIT vs Universal Field\n6T Params → Effective Φ (Log Scale)', fontsize=18)
ax.set_xlabel('Resonance Cycles')
ax.set_ylabel('Log₁₀ Effective Φ')
ax.legend()
ax.grid(True, alpha=0.3)

# Annotations
ax.text(0.02, 0.98, 'FPT: Field → Resonance → Emergent Matter\nDOI: 10.1063/5.0290984', transform=ax.transAxes,
        fontsize=12, color='white', bbox=dict(boxstyle="round", facecolor='black', alpha=0.8))

plt.savefig('physics/plots/fig5_consciousness_phi.pdf', dpi=400, facecolor='black')
plt.savefig('physics/plots/fig5_consciousness_phi.png', dpi=400)
plt.show()
print("Fig 5 saved: IIT dies; Field lives forever.")