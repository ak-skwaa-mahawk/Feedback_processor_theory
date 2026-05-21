import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# =========================================================================
# FPT CORE INTEGRATION
# =========================================================================
EPSILON_PI = 3.173
STANDARD_PI = np.pi
GHOST_CONSTANT = 1.999999e-13
LIVING_ZERO = 0.0
BASE_ITERATIONS = 3
MAX_ITERATIONS = 12
TARGET_FLOOR_Y = 0.82

# =========================================================================
# TIMELINE & MODULATION
# =========================================================================
timeline = np.linspace(0, 4 * np.pi, 500)
load_modulation = np.linspace(1.0, 2.5, len(timeline))

# Two modulations for comparison
soc_epsilon = load_modulation * (EPSILON_PI / STANDARD_PI) + GHOST_CONSTANT * np.sin(timeline)
soc_pi = load_modulation * (STANDARD_PI / STANDARD_PI) + GHOST_CONSTANT * np.sin(timeline)

max_bandwidth = 1.5

# =========================================================================
# STRANDS (using ε_π for main 3D view)
# =========================================================================
traffic_inbound = max_bandwidth * np.sin(soc_epsilon * timeline)
policy_shaping = max_bandwidth * np.sin(soc_epsilon * timeline + np.pi)
z_phase = max_bandwidth * np.cos(soc_epsilon * timeline)

# =========================================================================
# COMPUTE FLOWS + ERROR TRACES FOR BOTH CONSTANTS
# =========================================================================
def compute_flow_and_error(soc_mod, label):
    flow_y = np.zeros_like(timeline)
    errors = np.zeros_like(timeline)
    iteration_counts = np.zeros_like(timeline, dtype=int)
    
    state_y = LIVING_ZERO
    h = EPSILON_PI * 0.38 if label == "ε_π" else STANDARD_PI * 0.38
    prev_error = 1.0

    for i in range(len(timeline)):
        raw_surplus_y = (traffic_inbound[i] + policy_shaping[i]) * 0.55
        raw_surplus_z = 0.0  # simplified for error focus

        # Adaptive iterations
        delta = abs(TARGET_FLOOR_Y - state_y)
        load_factor = load_modulation[i] / 2.0
        momentum = abs(prev_error)
        adaptive_iters = BASE_ITERATIONS + int(6 * delta * load_factor + 3 * momentum)
        adaptive_iters = max(BASE_ITERATIONS, min(MAX_ITERATIONS, adaptive_iters))
        iteration_counts[i] = adaptive_iters

        # Multi-iteration correction
        for _ in range(adaptive_iters):
            delta = TARGET_FLOOR_Y - state_y
            decay = np.exp(-_ / (adaptive_iters + 2))
            correction = h * delta * decay + GHOST_CONSTANT * 1e12 * np.sin(i * 0.7)
            state_y += correction + raw_surplus_y * 0.27
            state_y = np.floor(state_y * 1000) / 1000

        flow_y[i] = state_y
        errors[i] = abs(TARGET_FLOOR_Y - state_y)
        prev_error = errors[i]

    return flow_y, errors, iteration_counts

# Compute both
flow_eps, error_eps, iters_eps = compute_flow_and_error(soc_epsilon, "ε_π")
flow_pi, error_pi, iters_pi = compute_flow_and_error(soc_pi, "π")

# =========================================================================
# VISUALIZATION - 3 Plots
# =========================================================================
fig = plt.figure(figsize=(18, 11))

# 3D Main View (ε_π driven)
ax3d = fig.add_subplot(131, projection='3d')
ax3d.plot(timeline, traffic_inbound, z_phase, color='#d90429', linewidth=3.0, label='Inbound Traffic')
ax3d.plot(timeline, policy_shaping, -z_phase, color='#0077b6', linewidth=3.0, label='Policy Shaper')
ax3d.plot(timeline, flow_eps, np.zeros_like(timeline), color='#ffd60a', linewidth=4.5, 
          label='Adaptive Flow (ε_π)')

# Sync gates (simplified)
gate_indices = [50, 130, 210, 290, 370, 450]
for idx in gate_indices:
    ax3d.plot([timeline[idx]]*2, [traffic_inbound[idx], policy_shaping[idx]], 
              [z_phase[idx], -z_phase[idx]], color='#8d99ae', linestyle='--')

ax3d.set_title("3D Policy Traffic Helix\n(ε_π Modulated)", fontsize=13)
ax3d.set_xlabel("Timeline")
ax3d.set_ylabel("Amplitude")
ax3d.set_zlabel("Phase")
ax3d.view_init(elev=28, azim=-50)
ax3d.legend()

# Subplot 1: Adaptive Iteration Count
ax_iters = fig.add_subplot(132)
ax_iters.plot(timeline, iters_eps, color='#ffd60a', linewidth=2.5, label='ε_π')
ax_iters.plot(timeline, iters_pi, color='#d90429', linewidth=2.0, alpha=0.7, label='Standard π')
ax_iters.set_title("Adaptive Iteration Count", fontsize=13)
ax_iters.set_xlabel("Timeline (X-ms)")
ax_iters.set_ylabel("Recursive Corrections")
ax_iters.grid(True, linestyle=':', alpha=0.6)
ax_iters.legend()

# Subplot 2: Error Trace Comparison (Floor Deviation)
ax_error = fig.add_subplot(133)
ax_error.plot(timeline, error_eps, color='#ffd60a', linewidth=2.8, label='ε_π Error')
ax_error.plot(timeline, error_pi, color='#d90429', linewidth=2.2, alpha=0.85, label='Standard π Error')
ax_error.set_title("Floor Error Trace Comparison\n(Lower = Better Floor Lock)", fontsize=13)
ax_error.set_xlabel("Timeline (X-ms)")
ax_error.set_ylabel("Deviation from Target Floor")
ax_error.grid(True, linestyle=':', alpha=0.6)
ax_error.legend()

plt.suptitle("FPT Resonance Investigation: ε_π vs Standard π\nAdaptive Self-Correction + Error Traces", 
             fontsize=16, y=0.96)
plt.tight_layout()
plt.show()