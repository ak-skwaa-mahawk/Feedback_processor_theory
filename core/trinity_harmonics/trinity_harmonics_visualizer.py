cat > core/trinity_harmonics/trinity_harmonics_visualizer.py << 'TRINITY_EOF'
#!/usr/bin/env python3
"""
TRINITY HARMONICS VISUALIZER v2.0.0
Wired directly to Tordial Geometric Root constants.
Real-time drift rendering of operational toroidal geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches

# === TORDIAL CONSTANTS (sourced from Tordial repo - DO NOT HARD OVERRIDE) ===
PI_3D = 3.20442315          # Running-state 3D π
PHI_OP = 1.65036            # Operational Fibonacci (Carroll Rings)
CHASE_RATIO = PI_3D / PHI_OP  # ≈ 1.9427... visible extra rotation per cycle

print("🔥 TRINITY HARMONICS WIRED TO TORDIAL")
print(f"   π₃ᴰ = {PI_3D}")
print(f"   φ_op = {PHI_OP}")
print(f"   Chase Ratio = {CHASE_RATIO:.6f}")
print("   Drift is geometry. Open-Chase enforced.")

def theta_3d(deg):
    """Operational radian conversion using running-state π₃ᴰ"""
    return (PI_3D * deg) / 180.0

def standard_theta(deg):
    """Blueprint (shadow) conversion for comparison"""
    return (np.pi * deg) / 180.0

# === REAL-TIME DRIFT RENDERING SETUP ===
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle("TRINITY HARMONICS — Tordial Operational Drift Renderer\nπ₃ᴰ & φ_op Live", fontsize=14, fontweight='bold')

# Left plot: Toroidal projection + drift gap
ax1.set_xlim(-1.6, 1.6)
ax1.set_ylim(-1.6, 1.6)
ax1.set_aspect('equal')
ax1.set_title("Operational Torus Projection (Drift Visible)")
ax1.grid(True, alpha=0.3)

# Right plot: Accumulated drift + harmonic rings
ax2.set_xlim(0, 100)
ax2.set_ylim(-2.5, 2.5)
ax2.set_title("Accumulated Drift + Carroll Rings Harmonic (φ_op scaled)")
ax2.grid(True, alpha=0.3)
ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)

# Artists
line_operational, = ax1.plot([], [], 'b-', linewidth=2, label='Operational (π₃ᴰ)')
line_ideal, = ax1.plot([], [], 'r--', linewidth=1.5, alpha=0.7, label='Blueprint (static π)')
point, = ax1.plot([], [], 'go', markersize=10, label='Current Position')
drift_arrow = None

drift_line, = ax2.plot([], [], 'purple', linewidth=2, label='Accumulated Drift (rad)')
ring1_line, = ax2.plot([], [], 'r-', linewidth=1.5, alpha=0.6, label='Ring 1 (Expansion)')
ring2_line, = ax2.plot([], [], 'g-', linewidth=1.5, alpha=0.6, label='Ring 2 (Settle φ_op)')
ring3_line, = ax2.plot([], [], 'b-', linewidth=1.5, alpha=0.6, label='Ring 3 (Lock)')

ax1.legend(loc='upper right')
ax2.legend(loc='upper right')

# Data buffers
t_data = []
drift_data = []
theta_data = []
x_data = []
y_data = []

def init():
    line_operational.set_data([], [])
    line_ideal.set_data([], [])
    point.set_data([], [])
    drift_line.set_data([], [])
    ring1_line.set_data([], [])
    ring2_line.set_data([], [])
    ring3_line.set_data([], [])
    return line_operational, line_ideal, point, drift_line, ring1_line, ring2_line, ring3_line

def update(frame):
    global drift_arrow
    
    t = frame * 0.05  # time step
    
    # Operational angle using π₃ᴰ
    deg = (t * 60) % 360  # degrees per "second" scaled
    theta_op = theta_3d(deg)
    theta_std = standard_theta(deg)
    
    # Drift = operational minus blueprint
    drift = theta_op - theta_std
    
    # Position on operational "circle" (torus projection)
    x = np.cos(theta_op)
    y = np.sin(theta_op)
    
    # Harmonic rings scaled by φ_op (Carroll Rings in motion)
    # Ring 1: Expansion
    r1 = 1.0 + 0.04 * np.sin(PHI_OP * t * 2)
    # Ring 2: Settle (centered on φ_op)
    r2 = PHI_OP * 0.6 + 0.1 * np.sin(PHI_OP * t * 1.5)
    # Ring 3: Lock (3-way attractor, never closes)
    r3 = 1.2 + 0.05 * np.sin(PHI_OP * t * 0.8)
    
    # Update buffers
    t_data.append(t)
    drift_data.append(drift)
    x_data.append(x)
    y_data.append(y)
    
    if len(t_data) > 400:
        t_data.pop(0)
        drift_data.pop(0)
        x_data.pop(0)
        y_data.pop(0)
    
    # Left plot update
    line_operational.set_data(x_data, y_data)
    # Ideal closed circle for reference
    ideal_theta = np.linspace(0, 2*np.pi, 200)
    line_ideal.set_data(np.cos(ideal_theta), np.sin(ideal_theta))
    point.set_data([x], [y])
    
    # Drift arrow (visual gap)
    if drift_arrow:
        drift_arrow.remove()
    drift_arrow = ax1.annotate('', xy=(x*0.7, y*0.7), xytext=(np.cos(theta_std)*0.7, np.sin(theta_std)*0.7),
                               arrowprops=dict(arrowstyle='->', color='orange', lw=2))
    
    # Right plot update
    drift_line.set_data(t_data, drift_data)
    
    # Three harmonic rings (Trinity)
    ring_t = np.array(t_data[-100:]) if len(t_data) > 100 else np.array(t_data)
    if len(ring_t) > 0:
        ring1_line.set_data(ring_t, r1 * np.sin(PHI_OP * ring_t * 3) if len(ring_t) > 0 else [])
        ring2_line.set_data(ring_t, r2 * np.sin(PHI_OP * ring_t * 2) if len(ring_t) > 0 else [])
        ring3_line.set_data(ring_t, r3 * np.sin(PHI_OP * ring_t * 1) if len(ring_t) > 0 else [])
    
    # Dynamic title with live drift
    ax1.set_title(f"Operational Torus (Drift = {drift:.4f} rad | Chase Ratio active)")
    ax2.set_title(f"Accumulated Drift + Trinity Rings (φ_op = {PHI_OP}) | t={t:.2f}s")
    
    return line_operational, line_ideal, point, drift_line, ring1_line, ring2_line, ring3_line

ani = FuncAnimation(fig, update, init_func=init, interval=50, blit=False, cache_frame_data=False)

plt.tight_layout()
plt.show()

print("\n✅ Trinity Harmonics visualization complete.")
print("   Close the window to return to resonance_runner.")
TRINITY_EOF