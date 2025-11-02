# peps_d9_particle_trails.py
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
TRAIL_LENGTH = 15  # Number of past frames to show

# === Precompute key χ states ===
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

# === Easing + Interpolation ===
def ease_in_out_cubic(t):
    return 4 * t**3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def interpolate(frame):
    raw = frame / (FRAMES - 1)
    eased = ease_in_out_cubic(raw)
    chi_float = 8 + eased * (32 - 8)
    
    chi_low = max([c for c in key_chis if c <= chi_float], default=key_chis[0])
    chi_high = min([c for c in key_chis if c >= chi_float], default=key_chis[-1])
    
    if chi_low == chi_high:
        return chi_float, entropy_maps[chi_low], R_values[chi_low], S_values[chi_low]
    
    w = (chi_float - chi_low) / (chi_high - chi_low)
    Z = (1 - w) * entropy_maps[chi_low] + w * entropy_maps[chi_high]
    R = (1 - w) * R_values[chi_low] + w * R_values[chi_high]
    S = SUBSYS * cp.log(2).get() * (chi_float / CHI_MAX)
    
    return chi_float, Z, R, S

# === Trail Buffer ===
trail_buffer = []
X, Y = np.meshgrid(np.arange(L), np.arange(L))

# === Animation ===
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

def update(frame):
    ax.cla()
    chi_float, Z, R, S = interpolate(frame)
    
    # === Current Surface (High opacity) ===
    surf = ax.plot_surface(
        X, Y, Z, cmap='plasma', alpha=0.95, linewidth=0,
        rcount=120, ccount=120, shade=True, antialiased=True
    )
    
    # === Data Qubits (Glowing) ===
    data_x, data_y = np.meshgrid(np.arange(0, L, 2), np.arange(0, L, 2))
    ax.scatter(data_x, data_y, Z[::2, ::2], c='cyan', s=100, depthshade=False,
               edgecolors='white', linewidth=1, alpha=1.0, zorder=10)

    # === Particle Trails (Past Entropy) ===
    trail_buffer.append(Z.copy())
    if len(trail_buffer) > TRAIL_LENGTH:
        trail_buffer.pop(0)
    
    for i, past_Z in enumerate(trail_buffer[:-1]):
        alpha = 0.1 + 0.6 * (i / (len(trail_buffer) - 1))  # Fade out
        color = plt.cm.plasma(alpha)
        ax.plot_surface(X, Y, past_Z, color=color, alpha=alpha*0.3,
                        rcount=60, ccount=60, shade=False, zorder=i)

    # === Labels & Status ===
    ax.set_xlabel('X Lattice')
    ax.set_ylabel('Y Lattice')
    ax.set_zlabel('S_local')
    ax.set_zlim(0, np.log(CHI_MAX) + 0.7)
    
    status = "AGI SOVEREIGN" if R > 0.997 and S > 17 else "VETO"
    color = 'lime' if status == "AGI SOVEREIGN" else 'red'
    
    ax.set_title(
        f'Ψ-PEPS d=9 | χ={chi_float:.1f}/{CHI_MAX} | S={S:.2f} | R={R:.6f}\n'
        f'Status: {status} | Trail: {len(trail_buffer)} frames',
        color=color, fontsize=15, pad=40,
        bbox=dict(boxstyle="round,pad=1", facecolor='black', alpha=0.8)
    )
    
    # === Cinematic Camera ===
    eased = ease_in_out_cubic(frame / (FRAMES - 1))
    azim = 30 + eased * 120
    elev = 30 + np.sin(eased * np.pi) * 20
    ax.view_init(elev=elev, azim=azim)

    return surf,

# === Run ===
ani = FuncAnimation(fig, update, frames=FRAMES, interval=80, blit=False, repeat=True)
# ani.save('peps_chi_trails.mp4', writer='ffmpeg', fps=30, dpi=180)
plt.show()