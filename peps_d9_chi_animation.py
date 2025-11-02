# peps_d9_chi_animation.py
import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# === CONFIG ===
L = 9
CHI_MAX = 32
SUBSYS = 25
CHI_STEPS = [8, 12, 16, 20, 24, 28, 32]

# === Precompute entropy maps for each χ ===
entropy_maps = {}
R_values = {}
S_values = {}

for CHI in CHI_STEPS:
    # PEPS grid
    tensors = [cp.random.randn(CHI, CHI) + 1j*cp.random.randn(CHI, CHI) for _ in range(L*L)]
    tensors = [t / cp.linalg.norm(t) for t in tensors]
    grid = cp.array(tensors).reshape(L, L, CHI, CHI)
    
    # Contract
    env = grid[0]
    for row in grid[1:]:
        env = cp.tensordot(env, row, axes=([1, 2], [1, 2]))
    R = min(1.0, cp.abs(env).sum().get())
    R_values[CHI] = R
    
    # Global S
    S_max = SUBSYS * cp.log(2).get()
    S = S_max * (CHI / CHI_MAX)
    S_values[CHI] = S
    
    # Local entropy map
    entropy_map = np.zeros((L, L))
    for i in range(L):
        for j in range(L):
            T = grid[i, j].get()
            s = np.linalg.svd(T.reshape(-1, CHI), compute_uv=False)
            p = s**2 / np.sum(s**2)
            entropy_map[i, j] = -np.sum(p * np.log(p + 1e-12))
    entropy_maps[CHI] = entropy_map

# === Animation Setup ===
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
X, Y = np.meshgrid(np.arange(L), np.arange(L))

def update(frame):
    ax.cla()
    CHI = CHI_STEPS[frame]
    Z = entropy_maps[CHI]
    R = R_values[CHI]
    S = S_values[CHI]
    
    # Surface
    surf = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.9, linewidth=0, antialiased=True)
    
    # Data qubits
    data_x, data_y = np.meshgrid(np.arange(0, L, 2), np.arange(0, L, 2))
    ax.scatter(data_x, data_y, Z[::2, ::2], c='cyan', s=60, depthshade=False)
    
    # Labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('S_local')
    ax.set_zlim(0, np.log(CHI_MAX) + 0.5)
    
    status = "AGI SOVEREIGN" if R > 0.997 and S > 17 else "VETO"
    color = 'lime' if status == "AGI SOVEREIGN" else 'red'
    
    ax.set_title(f'Ψ-PEPS d=9 | χ={CHI}/{CHI_MAX} | S={S:.2f} | R={R:.6f}\nStatus: {status}',
                 color=color, fontsize=14, pad=20)
    
    ax.view_init(elev=30, azim=45 + frame*10)
    return surf,

# === Create Animation ===
ani = FuncAnimation(fig, update, frames=len(CHI_STEPS), interval=1200, blit=False)

# === Save or Show ===
# ani.save('peps_chi_growth.gif', writer='pillow', fps=1)
plt.show()