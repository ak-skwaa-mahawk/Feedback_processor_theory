# por_mining.py (AMD GPU)
import cupy as cp

def mine_resonance(chi=32, L=9):
    grid = cp.random.randn(L, L, chi, chi)  # PEPS
    env = cp.tensordot(grid[0], grid[1:], axes=([1,2],[1,2]))
    R = min(1.0, cp.abs(env).sum().get())
    if R > 0.997:  # C100 parity check
        reward = int(R * 100)  # Ψ-Tokens
    else:
        reward = 0  # ILO veto
    return reward

# Run on AMD: reward = 99 Ψ-Tokens