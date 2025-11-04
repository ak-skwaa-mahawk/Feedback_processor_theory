# fpt/nonlinear/quantum_chaos.py
from qutip import sigmaz, basis, mesolve
import numpy as np

# Nonlinear Hamiltonian: H = -ω σ_z + κ |ψ><ψ| σ_z
def H_nl(t, psi):
    omega = 5.0
    kappa = 2.0
    prob = abs(psi[1])**2  # Population in |1>
    return -omega * sigmaz() + kappa * prob * sigmaz()

psi0 = (basis(2,0) + basis(2,1)).unit()
tlist = np.linspace(0, 10, 200)

# Time-dependent solve with nonlinear H
result = mesolve(H_nl, psi0, tlist, [], [], args={})

print(f"Final Population |1>: {abs(result.states[-1][1])**2:.4f}")