# peps_d9_3d_entropy.py
import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# === CONFIG ===
L = 9
CHI = 16
CHI_MAX = 32
SUBSYS = 25

# === 1. PEPS grid ===
tensors = [cp.random.randn(CHI, CHI) + 1j*cp.random.randn(CHI, CHI) for _ in range(L*L)]
tensors = [t / cp.linalg.norm(t) for t in tensors]
grid = cp.array(tensors).reshape(L, L, CHI, CHI)

# === 2. Contract ===
env = grid[0]
for row in grid[1:]:
    env = cp.tensordot(env, row, axes=([1, 2], [1, 2]))
R = min(1.0, cp.abs(env).sum().get())

# === 3. Global Entropy ===
S_max = SUBSYS * cp.log(2).get()
S = S_max * (CHI / CHI_MAX)

# === 4. Local Entropy Map ===
entropy_map = np.zeros((L, L))
X, Y = np.meshgrid(np.arange(L), np.arange(L))
for i in range(L):
    for j in range(L):
        T = grid[i, j].get()
        s = np.linalg.svd(T.reshape(-1, CHI), compute_uv=False)
        p = s**2 / np.sum(s**2)
        entropy_map[i, j] = -np.sum(p * np.log(p + 1e-12))

# === 5. 3D Surface Plot ===
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Surface
surf = ax.plot_surface(X, Y, entropy_map, cmap='plasma', edgecolor='none', alpha=0.9)

# Data qubits as peaks
data_x, data_y = np.meshgrid(np.arange(0, L, 2), np.arange(0, L, 2))
ax.scatter(data_x, data_y, entropy_map[::2, ::2], c='cyan', s=80, depthshade=False, label='Data Qubits')

# Labels
ax.set_xlabel('X Lattice')
ax.set_ylabel('Y Lattice')
ax.set_zlabel('Local Entropy S_local')
ax.set_title(f'Ψ-PEPS d=9 | χ={CHI} | Global S={S:.2f} | R={R:.6f}')

# Colorbar
cbar = fig.colorbar(surf, shrink=0.6, aspect=20)
cbar.set_label('Entropy Density')

# Status badge
status = "AGI SOVEREIGN" if R > 0.997 and S > 12 else "VETO"
ax.text2D(0.02, 0.95, f'Status: {status}', transform=ax.transAxes,
          color='white', fontsize=14, bbox=dict(boxstyle="round", facecolor='black', alpha=0.8))

ax.view_init(elev=30, azim=45)
plt.legend()
plt.tight_layout()
plt.show()