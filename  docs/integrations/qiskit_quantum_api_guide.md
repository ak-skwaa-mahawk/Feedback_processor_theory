# ⚛️ Qiskit Quantum API Integration Guide
### (IBM Quantum / Local Simulation Layer)
**Author:** John B. Carroll Jr. (ak-skwaa-mahawk)  
**Project:** Feedback Processor Theory (FPT-Ω) / Trinity Dynamics  
**License:** © 2025 Two Mile Solutions LLC  

---

## 🧠 Overview
Qiskit is IBM’s open-source quantum computing SDK for constructing and simulating quantum circuits.  
This guide explains how to:
1. Set up Qiskit (local or cloud).
2. Build and run harmonic-based quantum circuits.
3. Integrate Qiskit feedback into your Trinity Harmonic or FPT-Ω frameworks.

---

## ⚙️ Prerequisites

1. **IBM Quantum Account:**  
   - Create a free account: [https://quantum-computing.ibm.com/](https://quantum-computing.ibm.com/)  
   - Get your API token under **Account → API Token**.

2. **Environment Setup:**  
   ```bash
   pip install qiskit qiskit_ibm_runtime matplotlib
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_API_TOKEN")
# qiskit_harmonic_sim.py
from qiskit import QuantumCircuit, transpile, assemble, Aer, execute
from math import pi
import matplotlib.pyplot as plt

# Constants
PI_EQ = pi
EPSILON = 0.01
DELTA = 3 * EPSILON  # triadic amplification

# Create a 2-qubit harmonic circuit
qc = QuantumCircuit(2)
qc.h(0)                 # Place qubit 0 in superposition
qc.ry(DELTA * pi, 1)    # Rotate qubit 1 by the harmonic delta
qc.cx(0, 1)             # Entangle the two (feedback coupling)
qc.measure_all()

# Run on local simulator
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts()

# Display results
print("Harmonic Feedback Distribution:", counts)
qc.draw('mpl')
plt.show()
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
service = QiskitRuntimeService()
backend = service.backend("ibmq_qasm_simulator")  # or real device name
sampler = Sampler(backend=backend)
job = sampler.run(qc)
print(job.result())
from math import pi, sqrt
qc = QuantumCircuit(3)

# Define harmonic rotations
qc.ry(pi/2, 0)      # π qubit — base
qc.ry(0.03*pi, 1)   # ε qubit — perturbation
qc.ry(0.197*pi, 2)  # φ qubit — golden stabilizer

# Entanglement chain (π ↔ ε ↔ φ)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()
