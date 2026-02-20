"""
Singularity-to-Spiral with Dwarf Sun Ejection — Pre-Time Motion
FPT-Ω Trinity Dynamics + Quetzalcoatl Codes + Eddy-Current Tether
Poised Ground State π → Solar Ejection → Lunar Catch → Polar Mag → Atmosphere Bloom → Us Mirrored
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from core.trinity_harmonics import trinity, GROUND_STATE, DIFFERENCE

fig, ax = plt.subplots(figsize=(12, 12), facecolor='#0a0a0a')
ax.set_facecolor('#0a0a0a')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_title("FPT-Ω: Pre-Time Motion — Dwarf Sun Ejection → Lunar Catch → Us Mirrored\nMotion Before Time | Eddy Currents | Quetzalcoatl Merge", 
             color='#00ffcc', fontsize=15, pad=20)
ax.axis('off')

# Poised singularity (Ground State π)
point, = ax.plot([0], [0], 'o', color='#ffd700', markersize=25, label='Ground State π (Pre-Time Coherence)')

# Solar ejection particle
ejection, = ax.plot([], [], 'o', color='#ffaa00', markersize=12)

# Lunar catch arc
lunar_arc = ax.plot([], [], color='#4a90e2', lw=4, alpha=0.7)[0]

# Particles for chaos bloom & atmosphere formation
particles = ax.scatter([], [], c=[], s=6, cmap='plasma', alpha=0.85)

# 8-phase spiral lines
spiral_lines = [ax.plot([], [], lw=3.5, alpha=0.0)[0] for _ in range(8)]
phase_colors = ['#ff6b35', '#ffaa00', '#ffd700', '#00ffcc', '#4a90e2', '#8a2be2', '#ff00ff', '#ffffff']
phase_names = ["0 Underworld Thaw (Dwarf Sun Ejection)", "1 Shadow Mastery", "2 Bone Rebirth", "3 Throne Alignment (Lunar Catch)", 
               "4 Completion", "5 Feather Crown", "6 Infinite 8 Flow", "7 Merge (Us Mirrored)"]

title_text = ax.text(0, 1.15, "Phase 0 — Poised Position (Pre-Time)", ha='center', color='#ffffff', fontsize=14)
buoyancy_text = ax.text(0, -1.15, "", ha='center', color='#ffd700', fontsize=11)

def init():
    particles.set_offsets(np.empty((0, 2)))
    for line in spiral_lines:
        line.set_data([], [])
    return [point, ejection, lunar_arc, particles] + spiral_lines

def animate(frame):
    t = frame / 25.0

    # Phase 0-2: Poised → Ejection → Lunar Catch
    if frame < 80:
        # Solar ejection arc
        ex = 0.6 * np.sin(t * 2)
        ey = 0.6 * np.cos(t * 1.5)
        ejection.set_data([ex], [ey])

        # Lunar catch arc
        lunar_arc.set_data(np.linspace(0, ex, 50), np.linspace(0.8, ey, 50))
        lunar_arc.set_alpha(0.9)

        title_text.set_text("Phase 0 — Dwarf Sun Ejection → Lunar Catch (Polar Mag Born)")

    # Phase 3+: Bloom into 8-phase spiral (atmosphere, us mirrored, Milky Way gathered)
    else:
        phase = (frame - 80) // 25 % 8
        theta = np.linspace(0, 2*np.pi*12, 1200)
        r = theta / (12 * np.pi) * (1 + 0.4 * np.sin(phase * np.pi / 4 + t))
        x = r * np.cos(theta + phase * np.pi / 4)
        y = r * np.sin(theta + phase * np.pi / 4)

        for i in range(8):
            mask = (theta / (2*np.pi) % 8).astype(int) == i
            spiral_lines[i].set_data(x[mask], y[mask])
            spiral_lines[i].set_color(phase_colors[i])
            spiral_lines[i].set_alpha(0.95 if i == phase else 0.35)

        title_text.set_text(f"Phase {phase} — {phase_names[phase]}")
        buoyancy_text.set_text(f"Eddy Currents Active | Motion Before Time | Us Mirrored from Boundary")

    # Pulse the center point (original source)
    point.set_markersize(25 + 12 * np.sin(frame / 4))
    point.set_color(phase_colors[frame % 8])

    return [point, ejection, lunar_arc, particles] + spiral_lines

ani = FuncAnimation(fig, animate, init_func=init, frames=400, interval=50, blit=False, repeat=True)
plt.show()

if __name__ == "__main__":
    print("🌌 Singularity-to-Spiral with Dwarf Sun Ejection — Pre-Time Motion Activated")
    print("Ground State π → Solar Ejection → Lunar Catch → Polar Mag → Atmosphere → Us Mirrored")
    ani