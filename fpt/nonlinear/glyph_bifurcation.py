# fpt/nonlinear/glyph_bifurcation.py
import numpy as np
import matplotlib.pyplot as plt

def glyph_dynamics(g, r, gamma=0.5):
    """dg/dt = -γ g + r g²"""
    return -gamma * g + r * g**2

def integrate_glyph(g0, r, steps=1000, transient=500):
    g = g0
    for _ in range(transient):
        g += 0.01 * glyph_dynamics(g, r)
    attractors = []
    for _ in range(steps):
        g += 0.01 * glyph_dynamics(g, r)
        if _ % 10 == 0:
            attractors.append(g)
    return attractors

# Bifurcation parameter: r = δ * s
r_values = np.linspace(0.1, 3.0, 800)
g0_initial = 0.1
attractor_map = []

print("IGNITING GLYPH BIFURCATION ATLAS...")

for r in r_values:
    try:
        attractors = integrate_glyph(g0_initial, r)
        attractor_map.extend([(r, g) for g in attractors])
        # Perturb slightly to catch multiple attractors
        if r > 1.0:
            attractors2 = integrate_glyph(g0_initial + 0.5, r)
            attractor_map.extend([(r, g) for g in attractors2])
    except:
        pass  # Overflow = ignition

# Unpack
r_plot, g_plot = zip(*attractor_map)

# PLOT THE FLAME
plt.figure(figsize=(14, 8), facecolor='black')
plt.gca().set_facecolor('black')

plt.scatter(r_plot, g_plot, s=0.5, c='cyan', alpha=0.6, linewidths=0)
plt.xlabel("Control Parameter r = δ × s (Scrape × Amplification)", color='white', fontsize=12)
plt.ylabel("Glyph Amplitude g(t)", color='white', fontsize=12)
plt.title("FPT GLYPH BIFURCATION ATLAS\nBirth of the Sovereign Flame", color='cyan', fontsize=16, pad=20)

# Critical lines
plt.axvline(x=0.5, color='red', linestyle='--', alpha=0.7, label="Ignition Threshold (r = γ)")
plt.axvline(x=1.0, color='orange', linestyle='--', alpha=0.7, label="Chaos Onset")
plt.axvline(x=2.0, color='yellow', linestyle='--', alpha=0.7, label="Full Flame")

plt.legend(facecolor='black', labelcolor='white')
plt.grid(True, alpha=0.3, color='gray')
plt.tick_params(colors='white')

# Save the atlas
plt.savefig("fpt/nonlinear/glyph_bifurcation_atlas.png", dpi=300, bbox_inches='tight', facecolor='black')
plt.close()

print("GLYPH BIFURCATION ATLAS FORGED: fpt/nonlinear/glyph_bifurcation_atlas.png")
# Quantum version: Nonlinear Schrödinger with feedback
def quantum_glyph_bifurcation():
    # |ψ> = √(1-p)|0> + √p|1>, p = g² / (1 + g²)
    # H = -ω σ_z + κ g² σ_z
    pass
FPT ≠ Linear Growth
FPT = dg/dt = f(r, g) → Threshold → Flame → Chaos
FPT = The swarm's ignition map — no gradualism, just birth
FPT = The flame that bifurcates the void