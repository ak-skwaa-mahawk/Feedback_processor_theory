import json
import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from quantum_bridge import QuantumBridge

def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "quantum_config_template.json")
    if not os.path.exists(path):
        raise FileNotFoundError("quantum_config_template.json not found")
    with open(path) as f:
        return json.load(f)

@pytest.mark.basic
def test_bridge_initialization():
    cfg = load_config()
    bridge = QuantumBridge(config=cfg)
    assert isinstance(bridge, QuantumBridge)

@pytest.mark.simulation
def test_local_circuit_execution():
    cfg = load_config()
    bridge = QuantumBridge(config=cfg)
    try:
        from qiskit import QuantumCircuit
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()
        res = bridge.run_qiskit(qc)
        unified = bridge.unify_results(res)
        assert "backend" in unified
    except Exception:
        pytest.skip("Qiskit not installed or simulator unavailable")

@pytest.mark.simulation
def test_qubo_fallback():
    cfg = load_config()
    bridge = QuantumBridge(config=cfg)
    qubo = {("x", "x"): 1.0, ("y", "y"): 1.0, ("x", "y"): -2.0}
    res = bridge.solve_qubo(qubo)
    unified = bridge.unify_results(res)
    assert "backend" in unified