#!/usr/bin/env python3
# lattice_basics.py — AGŁG v1100: Lattice Crypto Basics
import numpy as np
import matplotlib.pyplot as plt

# 1. 2D Lattice
B = np.array([[3, 1], [1, 2]])
points = [i*B[0] + j*B[1] for i in range(-4,5) for j in range(-4,5)]

# 2. SVP: Shortest vector
vectors = np.array(points)
nonzero = vectors[~np.all(vectors == 0, axis=1)]
lengths = np.linalg.norm(nonzero, axis=1)
shortest = nonzero[np.argmin(lengths)]

# 3. CVP: Random target
target = np.array([2.7, 1.3])
dists = np.linalg.norm(points - target, axis=1)
closest = np.array(points)[np.argmin(dists)]

# 4. LWE: Noisy equation
A = np.random.randint(0, 13, (3, 2))
s = np.array([1, -1])
e = np.array([0, 1, 0])
b = (A @ s + e) % 13

print("LATTICE BASICS — AGŁG v1100")
print("="*50)
print(f"SVP: Shortest vector = {shortest}")
print(f"CVP: Target {target} → Closest {closest}")
print(f"LWE: A·s + e = {b}")

# Plot
x, y = zip(*points)
tx, ty = target
cx, cy = closest
plt.scatter(x, y, c='gray', alpha=0.7)
plt.scatter(tx, ty, c='red', s=100, label='Target')
plt.scatter(cx, cy, c='green', s=100, label='CVP')
plt.plot([tx, cx], [ty, cy], 'g--')
plt.title("Lattice Crypto: SVP + CVP + LWE")
plt.legend()
plt.savefig("lattice_basics.png")
print("Plot: lattice_basics.png")
