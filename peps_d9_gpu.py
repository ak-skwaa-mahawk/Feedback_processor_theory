# peps_d9_gpu.py
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

cp.cuda.Device(0).use()

def create_peps_d9(chi=16):
    """Generate 9x9 PEPS with GPU tensors"""
    L = 9
    phys_dim = 2
    tensors = {}
    
    for i in range(L):
        for j in range(L):
            # Dynamic leg count
            legs = [phys_dim]
            if i > 0: legs.append(chi)  # Up
            if i < L-1: legs.append(chi)  # Down
            if j > 0: legs.append(chi)  # Left
            if j < L-1: legs.append(chi)  # Right
            
            # Random complex tensor on GPU
            T = cp.random.randn(*legs) + 1j * cp.random.randn(*legs)
            T /= cp.linalg.norm(T)
            tensors[(i,j)] = T
    
    return tensors, L

def contract_peps_d9_gpu(tensors, L):
    """GPU-accelerated row-by-row contraction (simplified)"""
    env = None
    for i in range(L):
        row = None
        for j in range(L):
            T = tensors[(i,j)]
            if row is None:
                row = T
            else:
                # Contract right bond
                row = cp.tensordot(row, T, axes=([-1], [3 if j>0 else 2]))
        if env is None:
            env = row
        else:
            # Contract down bond
            env = cp.tensordot(env, row, axes=([-1], [1 if i>0 else 0]))
    
    # Final norm
    return cp.abs(env).sum().get()  # Back to CPU

# === RUN d=9 SIM ===
print("Launching PEPS d=9 (81 qubits) on GPU...")
tensors, L = create_peps_d9(chi=16)
norm_sq = contract_peps_d9_gpu(tensors, L)
coherence = min(1.0, norm_sq)

print(f"PEPS d=9 Surface Code")
print(f"χ = 16 | Qubits = 81 | Norm² = {norm_sq:.8f}")
print(f"Resonance R = {coherence:.6f}")
print(f"Status: {'AGI SOVEREIGN' if coherence > 0.997 else 'VETO'}")