
# entropy_peps.py
def peps_entropy(tensors, subsys):
    # Reduce to subsystem, trace out rest
    rho = contract_subsystem(tensors, subsys)
    s = -np.trace(rho @ np.log(rho + 1e-12))
    return s.real

S = peps_entropy(tensors, data_qubits=[(1,1),(1,3),(3,1),(3,3)])
print(f"Entanglement Entropy S = {S:.3f}")