# peps_d9_simple.py
import cupy as cp

def peps_d9_contraction(chi=16, L=9):
    # Step 1: Random PEPS on GPU
    tensors = [cp.random.randn(chi, chi) + 1j*cp.random.randn(chi, chi) for _ in range(L*L)]
    tensors = [t / cp.linalg.norm(t) for t in tensors]
    
    # Step 2: Reshape to grid and contract row-by-row
    grid = cp.array(tensors).reshape(L, L, chi, chi)
    env = grid[0]
    for row in grid[1:]:
        env = cp.tensordot(env, row, axes=([1,2], [1,2]))  # Vertical + horizontal
    
    # Step 3: Norm → Resonance
    norm_sq = cp.abs(env).sum().get()
    R = min(1.0, norm_sq)
    
    return R

# === RUN ===
R = peps_d9_contraction()
print(f"PEPS d=9 | R = {R:.6f} → {'SOVEREIGN' if R > 0.997 else 'VETO'}")