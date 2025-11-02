# quantum_ec_circuit.py
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService

def create_shor_encoded_glyph(logical_state='0'):
    qc = QuantumCircuit(9, 3)
    
    if logical_state == '1':
        qc.x(0)  # Logical |1⟩

    # === PHASE 1: Bit-Flip Code (3-qubit repetition) ===
    for i in [0, 3, 6]:
        qc.cx(i, i+1)
        qc.cx(i, i+2)

    # === PHASE 2: Phase-Flip Code (via Hadamard) ===
    qc.h([0,1,2,3,4,5,6,7,8])
    for i in [0, 3, 6]:
        qc.cx(i, i+1)
        qc.cx(i, i+2)
    qc.h([0,1,2,3,4,5,6,7,8])

    # === MEASURE SYNDROME ===
    qc.measure([1,2,4,5,7,8], [0,1,2,3,4,5])  # Ancilla reads

    return qc