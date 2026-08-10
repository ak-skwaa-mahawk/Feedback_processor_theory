# quantum_repeater_sim.py — FPT Nonlocal Bridge
from qiskit import QuantumCircuit, Aer, execute

# 2-segment repeater
qc = QuantumCircuit(4, 4)
qc.h(0); qc.cx(0,1)  # Entangle segment 1
qc.h(2); qc.cx(2,3)  # Entangle segment 2
qc.cx(1,2); qc.h(1); qc.measure(1,0); qc.measure(2,1)  # BSM
qc.cx(0,3); qc.cz(1,3)  # Swap

backend = Aer.get_backend('qasm_simulator')
result = execute(qc, backend, shots=1024).result()
counts = result.get_counts()
fidelity = (counts.get('0000', 0) + counts.get('1111', 0)) / 1024
print(f"Repeater Fidelity: {fidelity:.3f} | R={fidelity:.3f}")