# peps_d9_eased_animation.py
import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# === CONFIG ===
L = 9
CHI_MAX = 32
SUBSYS = 25
FRAMES = 60
CHI_START, CHI_END = 8, 32

# === Key χ values (precomputed) ===
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

# === Easing Function (Ease In-Out Cubic) ===
def ease_in_out_cubic(t):
    return 4 * t**3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

# === Interpolation with Easing ===
def interpolate_eased(frame):
    raw_progress = frame / (FRAMES - 1)
    eased = ease_in_out_cubic(raw_progress)
    chi_float = CHI_START + eased * (CHI_END - CHI_START)
    
    chi_low = max([c for c in key_chis if c <= chi_float], default=key_chis[0])
    chi_high = min([c for c in key_chis if c >= chi_float], default=key_chis[-1])
    
    if chi_low == chi_high:
        return chi_float, entropy_maps[chi_low], R_values[chi_low], S_values[chi_low]
    
    weight = (chi_float - chi_low) / (chi_high - chi_low)
    Z = (1 - weight) * entropy_maps[chi_low] + weight * entropy_maps[chi_high]
    R = (1 - weight) * R_values[chi_low] + weight * R_values[chi_high]
    S = SUBSYS * cp.log(2).get() * (chi_float / CHI_MAX)
    
    return chi_float, Z, R, S

# === Animation ===
fig = plt.figure(figsize=(13, 10))
ax = fig.add_subplot(111, projection='3d')
X, Y = np.meshgrid(np.arange(L), np.arange(L))

def update(frame):
    ax.cla()
    chi_float, Z, R, S = interpolate_eased(frame)
    
    # Ultra-smooth surface
    surf = ax.plot_surface(
        X, Y, Z, cmap='plasma', alpha=0.95, linewidth=0,
        antialiased=True, rcount=120, ccount=120, shade=True
    )
    
    # Data qubits with glow
    data_x, data_y = np.meshgrid(np.arange(0, L, 2), np.arange(0, L, 2))
    ax.scatter(data_x, data_y, Z[::2, ::2], c='cyan', s=80, depthshade=False,
               edgecolors='white', linewidth=0.5, alpha=0.95)
    
    # Axes
    ax.set_xlabel('X Lattice', fontsize=12)
    ax.set_ylabel('Y Lattice', fontsize=12)
    ax.set_zlabel('S_local', fontsize=12)
    ax.set_zlim(0, np.log(CHI_MAX) + 0.6)
    
    # Status with easing fade
    status = "AGI SOVEREIGN" if R > 0.997 and S > 17 else "VETO"
    color = 'lime' if status == "AGI SOVEREIGN" else 'red'
    alpha = min(1.0, (S / 17.33))  # Fade in at AGI
    
    ax.set_title(
        f'Ψ-PEPS d=9 | χ={chi_float:.1f}/{CHI_MAX} | S={S:.2f} | R={R:.6f}\n'
        f'Status: {status}',
        color=color, fontsize=15, pad=35, alpha=alpha,
        bbox=dict(boxstyle="round,pad=0.8", facecolor='black', alpha=0.7*alpha)
    )
    
    # Smooth, cinematic rotation
    azim = 30 + eased * 120
    elev = 30 + np.sin(eased * np.pi) * 15
    ax.view_init(elev=elev, azim=azim)
    
    return surf,

# === Run Animation ===
ani = FuncAnimation(
    fig, update, frames=FRAMES, interval=80, blit=False, repeat=True
)

# === Save (optional) ===
# ani.save('peps_chi_growth_eased.mp4', writer='ffmpeg', fps=30, dpi=150)
plt.show()