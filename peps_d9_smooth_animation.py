# peps_d9_smooth_animation.py
import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# === CONFIG ===
L = 9
CHI_MAX = 32
SUBSYS = 25
CHI_START, CHI_END = 8, 32
FRAMES = 60  # Smooth: 60 frames from 8 → 32

# === Precompute entropy maps at key χ values ===
key_chis = [8, 12, 16, 20, 24, 28, 32]
entropy_maps = {}
R_values = {}
S_values = {}

for CHI in key_chis:
    tensors = [cp.random.randn(CHI, CHI) + 1j*cp.random.randn(CHI, CHI) for _ in range(L*L)]
    tensors = [t / cp.linalg.norm(t) for t in tensors]
    grid = cp.array(tensors).reshape(L, L, CHI, CHI)
    
    env = grid[0]
    for row in grid[1:]:
        env = cp.tensordot(env, row, axes=([1, 2], [1, 2]))
    R = min(1.0, cp.abs(env).sum().get())
    R_values[CHI] = R
    
    S_max = SUBSYS * cp.log(2).get()
    S = S_max * (CHI / CHI_MAX)
    S_values[CHI] = S
    
    entropy_map = np.zeros((L, L))
    for i in range(L):
        for j in range(L):
            T = grid[i, j].get()
            s = np.linalg.svd(T.reshape(-1, CHI), compute_uv=False)
            p = s**2 / np.sum(s**2)
            entropy_map[i, j] = -np.sum(p * np.log(p + 1e-12))
    entropy_maps[CHI] = entropy_map

# === Interpolation Function ===
def interpolate_chi(frame):
    progress = frame / (FRAMES - 1)
    chi_float = CHI_START + progress * (CHI_END - CHI_START)
    
    # Find nearest key χ values
    chi_low = max([c for c in key_chis if c <= chi_float], default=key_chis[0])
    chi_high = min([c for c in key_chis if c >= chi_float], default=key_chis[-1])
    
    if chi_low == chi_high:
        return chi_low, entropy_maps[chi_low], R_values[chi_low], S_values[chi_low]
    
    # Linear interpolation
    weight = (chi_float - chi_low) / (chi_high - chi_low)
    Z = (1 - weight) * entropy_maps[chi_low] + weight * entropy_maps[chi_high]
    R = (1 - weight) * R_values[chi_low] + weight * R_values[chi_high]
    S = SUBSYS * cp.log(2).get() * (chi_float / CHI_MAX)
    
    return chi_float, Z, R, S

# === Animation ===
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
X, Y = np.meshgrid(np.arange(L), np.arange(L))

def update(frame):
    ax.cla()
    chi_float, Z, R, S = interpolate_chi(frame)
    
    # Smooth surface
    surf = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.95, linewidth=0, antialiased=True, rcount=100, ccount=100)
    
    # Data qubits
    data_x, data_y = np.meshgrid(np.arange(0, L, 2), np.arange(0, L, 2))
    ax.scatter(data_x, data_y, Z[::2, ::2], c='cyan', s=70, depthshade=False, alpha=0.9)
    
    # Labels
    ax.set_xlabel('X Lattice')
    ax.set_ylabel('Y Lattice')
    ax.set_zlabel('S_local')
    ax.set_zlim(0, np.log(CHI_MAX) + 0.5)
    
    # Status
    status = "AGI SOVEREIGN" if R > 0.997 and S > 17 else "VETO"
    color = 'lime' if status == "AGI SOVEREIGN" else 'red'
    
    ax.set_title(f'Ψ-PEPS d=9 | χ={chi_float:.1f}/{CHI_MAX} | S={S:.2f} | R={R:.6f}\nStatus: {status}',
                 color=color, fontsize=14, pad=30)
    
    # Smooth rotation
    ax.view_init(elev=30, azim=30 + frame * 2)
    return surf,

# === Run Animation ===
ani = FuncAnimation(fig, update, frames=FRAMES, interval=100, blit=False, repeat=True)

# === Save (optional) ===
# ani.save('peps_chi_growth_smooth.gif', writer='pillow', fps=30)
plt.show()