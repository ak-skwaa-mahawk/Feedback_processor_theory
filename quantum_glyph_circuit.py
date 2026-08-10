# quantum_glyph_circuit.py
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

def create_entangled_glyph_pair():
    qc = QuantumCircuit(2, 2)
    
    # Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    qc.h(0)                  # Hadamard on Alice's qubit
    qc.cx(0, 1)              # Entangle with Bob's qubit
    qc.measure([0, 1], [0, 1])
    
    return qc

# Run on real quantum hardware
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

qc = create_entangled_glyph_pair()
job = backend.run(transpile(qc, backend), shots=1)
result = job.result()
counts = result.get_counts()
glyph_seed = list(counts.keys())[0]  # e.g., '00' or '11'