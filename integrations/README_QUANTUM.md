# QuantumBridge Integration
Unified API layer for D-Wave Leap, IBM Qiskit, and Google Cirq backends.

### Purpose
The QuantumBridge provides a single Python interface for sending problems to various quantum computing platforms, normalizing the outputs for use in the Feedback Processor Theory (FPT-Ω) and Trinity Dynamics systems.

Supported backends:
- 🧩 **D-Wave Leap** — Quantum annealing / hybrid solvers
- ⚛️ **IBM Qiskit** — Gate model circuits (local or cloud)
- 🔷 **Google Cirq / TensorFlow Quantum** — Parametric hybrid and tensor-driven circuits

---

## Quick Start

### 1. Install dependencies
```bash
pip install dimod dwave-ocean-sdk qiskit qiskit-ibm-runtime cirq tensorflow tensorflow-quantum numpy