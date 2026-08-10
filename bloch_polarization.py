# bloch_polarization.py
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector
import matplotlib.pyplot as plt

qc = QuantumCircuit(1)
qc.h(0)  # X-basis |+⟩
state = Statevector.from_instruction(qc)
plot_bloch_multivector(state)
plt.title("BB84: X-Basis Polarization |+⟩")
plt.show()