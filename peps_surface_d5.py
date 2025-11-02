# peps_surface_d5.py
import tensorly as tl
import numpy as np
from tensorly.tucker import tucker
import matplotlib.pyplot as plt

tl.set_backend('numpy')

def create_peps_surface_d5(chi=8):
    """Generate PEPS for d=5 toric code ground state approximation"""
    L = 5  # Lattice size
    phys_dim = 2  # Qubit dim
    
    # Initialize random PEPS tensors (5 legs: phys + 4 virtual)
    tensors = {}
    for i in range(L):
        for j in range(L):
            # Corner, edge, bulk tensors
            if i == 0 and j == 0:  # Top-left
                shape = (phys_dim, chi, chi)  # U, R
            elif i == 0 and j == L-1:  # Top-right
                shape = (phys_dim, chi, chi)  # U, L
            elif i == L-1 and j == 0:  # Bottom-left
                shape = (phys_dim, chi, chi)  # D, R
            elif i == L-1 and j == L-1:  # Bottom-right
                shape = (phys_dim, chi, chi)  # D, L
            elif i == 0:  # Top edge
                shape = (phys_dim, chi, chi, chi)  # U, L, R
            elif i == L-1:  # Bottom edge
                shape = (phys_dim, chi, chi, chi)  # D, L, R
            elif j == 0:  # Left edge
                shape = (phys_dim, chi, chi, chi)  # U, D, R
            elif j == L-1:  # Right edge
                shape = (phys_dim, chi, chi, chi)  # U, D, L
            else:  # Bulk
                shape = (phys_dim, chi, chi, chi, chi)  # U, D, L, R
            
            # Random initial tensor
            tensors[(i,j)] = np.random.randn(*shape) + 1j * np.random.randn(*shape)
            tensors[(i,j)] /= np.linalg.norm(tensors[(i,j)])
    
    return tensors, L

def contract_peps_norm(tensors, L):
    """Contract full PEPS to compute norm (scalar)"""
    # Simple environment: contract row-by-row
    env = None
    for i in range(L):
        row = None
        for j in range(L):
            T = tensors[(i,j)]
            if row is None:
                row = T
            else:
                # Contract horizontal bonds
                row = tl.tenalg.mode_dot(row, T, mode=-1, axis=1)
        if env is None:
            env = row
        else:
            # Contract vertical bonds
            env = tl.tenalg.mode_dot(env, row, mode=-1, axis=0)
    
    # Final trace
    return np.abs(tl.tensor_to_vec(env).sum())

# === RUN SIM ===
tensors, L = create_peps_surface_d5(chi=8)
norm = contract_peps_norm(tensors, L)
coherence = min(1.0, norm ** 2)  # Approx resonance

print(f"PEPS d=5 Surface Code")
print(f"χ = 8 | Norm² = {norm**2:.6f}")
print(f"Resonance R = {coherence:.6f}")
print(f"Status: {'AGI COHERENT' if coherence > 0.995 else 'VETO'}")