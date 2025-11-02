# surface_code_d3.py
from qiskit import QuantumCircuit
import numpy as np

def create_surface_code_d3():
    # 5 data qubits + 4 measure qubits = 9 total
    qc = QuantumCircuit(9, 4)
    
    # Initialize logical |0⟩_L = |00000⟩
    # (already in |0⟩)
    
    # === STABILIZER CYCLE ===
    # Z-stabilizers (plaquettes)
    qc.cz(0,1); qc.cz(0,3); qc.cz(0,4)  # M0
    qc.cz(1,2); qc.cz(1,4); qc.cz(1,5)  # M1
    qc.cz(3,4); qc.cz(4,5); qc.cz(4,7)  # M2
    qc.cz(4,5); qc.cz(5,6); qc.cz(5,8)  # M3
    
    # X-stabilizers (stars) — use ancillary measure qubits
    # We'll simulate with post-processing for now
    
    qc.measure([0,1,2,3,4,5,6,7,8], range(9))  # Full readout
    
    return qc