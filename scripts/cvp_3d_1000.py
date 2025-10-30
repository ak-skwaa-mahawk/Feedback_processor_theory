#!/usr/bin/env python3
# cvp_3d_1000.py — AGŁG v1000: CVP on 3D Lattice with 1000 Points
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import hashlib

# === 1. DEFINE 3D LATTICE BASIS ===
# A nice integer basis with some stretch
basis = np.array([
    [4, 1, 1],
    [1, 3, 1],
    [1, 1, 5]
], dtype=float)

# === 2. GENERATE 1000 LATTICE POINTS ===
print("GENERATING 1000 LATTICE POINTS...")
coeffs = np.array(np.meshgrid(
    np.arange(-5, 6),   # i
    np.arange(-5, 6),   # j
    np.arange(-5, 6)    # k
)).T.reshape(-1, 3)

lattice_points = np.dot(coeffs, basis.T)
lattice_points = lattice_points[:1000]  # Take first 1000
print(f"Generated {len(lattice_points)} points")

# === 3. PICK RANDOM TARGET t (not on lattice) ===
np.random.seed(łᐊᒥłł := 108)  # Ancestral seed
target = np.random.uniform(-20, 20, size=3) + np.array([0.7, 1.3, -0.9])
print(f"Target t: {target}")

# === 4. BRUTE-FORCE CVP: Find closest point ===
start = time.time()
distances = np.linalg.norm(lattice_points - target, axis=1)
closest_idx = np.argmin(distances)
closest_point = lattice_points[closest_idx]
min_distance = distances[closest_idx]
end = time.time()

print(f"\nCVP SOLUTION (1000 points):")
print(f"Closest point v: {closest_point}")
print(f"Distance ||t - v||: {min_distance:.6f}")
print(f"Time: {end - start:.3f}s")

# === 5. PROOF HASH (for Ordinals) ===
proof_data = f"{target}{closest_point}{min_distance}"
proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()
print(f"Proof Hash: {proof_hash}")

# === 6. 3D VISUALIZATION ===
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot lattice points
ax.scatter(lattice_points[:,0], lattice_points[:,1], lattice_points[:,2],
           c='lightgray', alpha=0.6, s=20, label="Lattice Λ")

# Plot target
ax.scatter(*target, c='red', s=200, label="Target t", marker='X')

# Plot closest
ax.scatter(*closest_point, c='green', s=200, label="CVP solution v", marker='D')

# Draw line
ax.plot([target[0], closest_point[0]],
        [target[1], closest_point[1]],
        [target[2], closest_point[2]], 'g--', linewidth=2)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('CVP in 3D Lattice — 1000 Points — AGŁG v1000')
ax.legend()

# Save
plt.savefig("cvp_3d_1000.png", dpi=150, bbox_inches='tight')
print("Plot saved: cvp_3d_1000.png")

# === 7. INSCRIPTION READY ===
inscription = f"""
CVP 3D — 1000 POINTS — AGŁG v1000
──────────────────────────────────
Target: {target}
Closest: {closest_point}
Distance: {min_distance:.6f}
Points: 1000
Time: {end-start:.3f}s
Proof Hash: {proof_hash}
IACA #2025-DENE-CVP-1000
WE ARE STILL HERE.
"""

Path("inscription_cvp_1000.txt").write_text(inscription)
print("Inscription ready: inscription_cvp_1000.txt")