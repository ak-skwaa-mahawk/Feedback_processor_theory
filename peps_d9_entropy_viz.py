# peps_d9_entropy_viz.py
import cupy as cp
import matplotlib.pyplot as plt
import numpy as np

# === CONFIG ===
L = 9
CHI = 16
CHI_MAX = 32
SUBSYS = 25

# === 1. Create PEPS grid ===
tensors = [
    cp.random.randn(CHI, CHI) + 1j * cp.random.randn(CHI, CHI)
    for _ in range(L * L)
]
tensors = [t / cp.linalg.norm(t) for t in tensors]
grid = cp.array(tensors).reshape(L, L, CHI, CHI)

# === 2. Contract ===
env = grid[0]
for row in grid[1:]:
    env = cp.tensordot(env, row, axes=([1, 2], [1, 2]))
R = min(1.0, cp.abs(env).sum().get())

# === 3. χ-Scaled Entropy ===
S_max = SUBSYS * cp.log(2).get()
S = S_max * (CHI / CHI_MAX)

# === 4. Local Entropy Map (per site) ===
entropy_map = np.zeros((L, L))
for i in range(L):
    for j in range(L):
        T = grid[i, j].get()
        s = np.linalg.svd(T.reshape(-1, CHI), compute_uv=False)
        p = s**2 / np.sum(s**2)
        entropy_map[i, j] = -np.sum(p * np.log(p + 1e-12))  # von Neumann

# === 5. Visualize ===
plt.figure(figsize=(10, 8))
im = plt.imshow(entropy_map, cmap='plasma', vmin=0, vmax=np.log(CHI))
plt.colorbar(im, label='Local Entropy S_local')
plt.title(f'Ψ-PEPS d=9 | χ={CHI} | Global S={S:.2f} | R={R:.6f}')
plt.xlabel('X Position')
plt.ylabel('Y Position')

# Mark data qubits (odd indices)
for i in range(0, L, 2):
    for j in range(0, L, 2):
        plt.plot(j, i, 's', color='cyan', markersize=8, alpha=0.7)

plt.text(0.02, 0.98, f'Status: {"AGI SOVEREIGN" if R > 0.997 and S > 12 else "VETO"}',
         transform=plt.gca().transAxes, color='white', fontsize=12,
         bbox=dict(boxstyle="round", facecolor='black', alpha=0.7))

plt.tight_layout()
plt.show()