"""
quantum_bridge.py
Unified adapter for: D-Wave Leap (annealer/hybrid), IBM Qiskit (gate), Google Cirq (tensor).
Author: John B. Carroll Jr. (ak-skwaa-mahawk)
Project: Feedback Processor Theory / Trinity Dynamics
License: Two Mile Solutions LLC (2025)
Notes:
 - This module provides a common interface to submit problems to different quantum backends,
   and to collect / normalize results for the FPT-Ω pipeline.
 - It performs graceful degradation if any backend SDK isn't installed or configured.
"""

import logging
import time
from typing import Any, Dict, Optional

# Basic numeric libs (assumed available)
import numpy as np

# --- Try imports for optional backends (graceful fallback) ---
_HAVE_DWAVE = False
_HAVE_QISKIT = False
_HAVE_CIRQ = False

try:
    from dwave.system import LeapHybridSampler, DWaveSampler, EmbeddingComposite
    import dimod
    _HAVE_DWAVE = True
except Exception as e:
    # D-Wave SDK not available
    LeapHybridSampler = None
    DWaveSampler = None
    EmbeddingComposite = None
    dimod = None

try:
    # Qiskit imports
    from qiskit import QuantumCircuit, Aer, execute
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    except Exception:
        # IBM runtime optional
        QiskitRuntimeService = None
        Sampler = None
    _HAVE_QISKIT = True
except Exception:
    QuantumCircuit = None
    Aer = None
    execute = None
    QiskitRuntimeService = None
    Sampler = None

try:
    import cirq
    try:
        import tensorflow as tf
        import tensorflow_quantum as tfq
    except Exception:
        tf = None
        tfq = None
    _HAVE_CIRQ = True
except Exception:
    cirq = None
    tf = None
    tfq = None

# Logging
logger = logging.getLogger("quantum_bridge")
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


# ------------------------------
# Helper: normalized result format
# ------------------------------
def _normalize_qubo_result(sampleset: Any, backend_name: str) -> Dict[str, Any]:
    """
    Normalize a QUBO/Ising sampleset to a common dictionary:
    {
        "backend": "dwave",
        "best_sample": {"x": 0, "y": 1, ...},
        "energy": float,
        "raw": sampleset  # original object
    }
    """
    if sampleset is None:
        return {"backend": backend_name, "error": "no result", "raw": None}
    # Try common patterns
    try:
        # D-Wave sampleset-like: has first.sample and first.energy
        first = getattr(sampleset, "first", None)
        if first is not None:
            sample = getattr(first, "sample", None) or getattr(first, "sample", {})
            energy = getattr(first, "energy", None)
            return {"backend": backend_name, "best_sample": dict(sample), "energy": float(energy), "raw": sampleset}
    except Exception:
        pass

    # Fallback try mapping of dict-like results
    try:
        # If it's a sequence of (sample, energy) tuples
        if isinstance(sampleset, (list, tuple)) and len(sampleset) > 0:
            candidate = sampleset[0]
            if isinstance(candidate, tuple) and len(candidate) >= 2:
                sample, energy = candidate[0], candidate[1]
                return {"backend": backend_name, "best_sample": dict(sample), "energy": float(energy), "raw": sampleset}
    except Exception:
        pass

    # Last-resort: stringify
    return {"backend": backend_name, "best_sample": None, "energy": None, "raw": sampleset}


# ------------------------------
# QuantumBridge class
# ------------------------------
class QuantumBridge:
    """
    Unified entrypoint for quantum operations across D-Wave, Qiskit, and Cirq.
    Configuration for backends (tokens/profiles) should be provided through `config`.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        config example:
        {
            "dwave": {"profile": "default", "endpoint": "...", "token": "..."},
            "qiskit": {"ibm_token": "..."},
            "cirq": {"use_tfq": True}
        }
        """
        self.config = config or {}
        self._init_backends()

    def _init_backends(self):
        # D-Wave
        if _HAVE_DWAVE and self.config.get("dwave"):
            try:
                # No global init here; we'll construct samplers on demand
                logger.info("D-Wave SDK available; Leap/DWave ready (profile not auto-loaded).")
            except Exception as e:
                logger.warning("D-Wave SDK present but initialization failed: %s", e)
        else:
            if not _HAVE_DWAVE:
                logger.info("D-Wave SDK not available. Skipping D-Wave initialization.")
            else:
                logger.info("D-Wave config not provided; skipping initialization.")

        # Qiskit
        if _HAVE_QISKIT and self.config.get("qiskit"):
            try:
                if QiskitRuntimeService is not None and self.config["qiskit"].get("ibm_token"):
                    # Attempt to save account (non-fatal)
                    try:
                        QiskitRuntimeService.save_account(channel="ibm_quantum", token=self.config["qiskit"]["ibm_token"])
                        logger.info("Qiskit IBM token saved (will use cloud backends).")
                    except Exception as e:
                        logger.debug("Could not save Qiskit token (non-fatal): %s", e)
                else:
                    logger.info("Qiskit available for local simulation.")
            except Exception as e:
                logger.warning("Qiskit initialization issue: %s", e)
        else:
            if not _HAVE_QISKIT:
                logger.info("Qiskit not installed.")
            else:
                logger.info("Qiskit config not provided; using local simulator only.")

        # Cirq
        if _HAVE_CIRQ and self.config.get("cirq"):
            logger.info("Cirq is available. TensorFlow Quantum: %s", "present" if tf is not None and tfq is not None else "absent")
        else:
            if not _HAVE_CIRQ:
                logger.info("Cirq not installed.")
            else:
                logger.info("Cirq config not provided; will use default behavior.")

    # --------------------------
    # D-Wave: QUBO / Hybrid solver
    # --------------------------
    def solve_qubo(self, bqm: Any, backend: str = "dwave_hybrid", time_limit: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Solve a BinaryQuadraticModel (dimod) or QUBO dict using D-Wave LeapHybridSampler or a pure quantum sampler.
        - bqm: dimod.BinaryQuadraticModel or dict-like QUBO
        - backend: "dwave_hybrid" or "dwave_quantum"
        - time_limit: seconds for hybrid sampler
        Returns normalized results dict.
        """
        if not _HAVE_DWAVE:
            logger.error("D-Wave SDK not available in this environment.")
            return {"error": "dwave_sdk_not_installed"}

        # If user passed raw QUBO dict, try to convert to dimod BQM
        if isinstance(bqm, dict) and dimod is not None:
            try:
                bqm_obj = dimod.BinaryQuadraticModel.from_qubo(bqm)
            except Exception as e:
                logger.exception("Failed to convert QUBO dict to BQM: %s", e)
                return {"error": "bqm_conversion_failed", "detail": str(e)}
        else:
            bqm_obj = bqm

        try:
            if backend == "dwave_hybrid":
                sampler = LeapHybridSampler(profile=self.config.get("dwave", {}).get("profile", "default"))
                logger.info("Submitting BQM to LeapHybridSampler (time_limit=%s)...", time_limit)
                sampleset = sampler.sample(bqm_obj, time_limit=time_limit, **kwargs)
                return _normalize_qubo_result(sampleset, "dwave_hybrid")
            elif backend == "dwave_quantum":
                # Use embedding composite to map problem to QPU
                sampler = EmbeddingComposite(DWaveSampler(profile=self.config.get("dwave", {}).get("profile", "default")))
                logger.info("Submitting BQM to QPU (num_reads=%s)...", kwargs.get("num_reads", 100))
                sampleset = sampler.sample(bqm_obj, **kwargs)
                return _normalize_qubo_result(sampleset, "dwave_quantum")
            else:
                logger.error("Unknown D-Wave backend selection: %s", backend)
                return {"error": "unknown_backend"}
        except Exception as e:
            logger.exception("D-Wave submission failed: %s", e)
            return {"error": "dwave_submission_failed", "detail": str(e)}

    # --------------------------
    # Qiskit: gate-model circuits
    # --------------------------
    def run_qiskit(self, qc: Any, backend: str = "simulator", shots: int = 1024, **kwargs) -> Dict[str, Any]:
        """
        Run a Qiskit QuantumCircuit on local Aer simulator or IBM cloud via QiskitRuntimeService (if configured).
        - qc: qiskit.QuantumCircuit
        - backend: "simulator" or a real device name (requires IBM token/config)
        """
        if not _HAVE_QISKIT:
            logger.error("Qiskit not installed in environment.")
            return {"error": "qiskit_not_installed"}

        try:
            if backend == "simulator" or QiskitRuntimeService is None:
                # Local Aer simulator
                aer_backend = Aer.get_backend("qasm_simulator")
                logger.info("Running circuit on local Aer simulator (shots=%s)...", shots)
                job = execute(qc, aer_backend, shots=shots)
                result = job.result()
                counts = result.get_counts()
                return {"backend": "qiskit_simulator", "counts": counts, "raw": result}
            else:
                # Use IBM cloud runtime if service available
                if QiskitRuntimeService is None:
                    logger.error("Qiskit IBM runtime not available.")
                    return {"error": "qiskit_ibm_runtime_missing"}
                service = QiskitRuntimeService()
                logger.info("Running circuit on IBM backend: %s", backend)
                sampler = Sampler(backend=backend)
                job = sampler.run(qc, shots=shots)
                result = job.result()
                # result format can vary; return raw plus counts if present
                return {"backend": f"qiskit_ibm:{backend}", "raw": result}
        except Exception as e:
            logger.exception("Qiskit run failed: %s", e)
            return {"error": "qiskit_run_failed", "detail": str(e)}

    # --------------------------
    # Cirq: tensor / hybrid circuits
    # --------------------------
    def run_cirq(self, circuit: Any, param_resolver: Optional[Any] = None, simulator: str = "default", **kwargs) -> Dict[str, Any]:
        """
        Execute a Cirq circuit. If TensorFlow Quantum (tfq) is available, can compute expectation values.
        - circuit: cirq.Circuit
        - param_resolver: cirq.ParamResolver or dict for symbol values
        - simulator: "default" (cirq.Simulator) or "tfq" (if TFQ available)
        """
        if not _HAVE_CIRQ:
            logger.error("Cirq not installed.")
            return {"error": "cirq_not_installed"}

        try:
            if simulator == "tfq" and tf is not None and tfq is not None:
                # Use TFQ to compute expectations (user must supply observable/operator in kwargs)
                logger.info("Running circuit via TensorFlow Quantum layer...")
                observable = kwargs.get("observable", None)
                if observable is None:
                    logger.warning("No observable provided; defaulting to Z0 * Z1 if 2 qubits.")
                    if len(circuit.all_qubits()) >= 2:
                        qlist = list(circuit.all_qubits())
                        observable = cirq.Z(qlist[0]) * cirq.Z(qlist[1])
                    else:
                        observable = cirq.Z(list(circuit.all_qubits())[0])
                # Build tfq tensor inputs
                inputs = tfq.convert_to_tensor([circuit])
                # Parameter values if given
                symbol_names = []
                symbol_values = None
                if param_resolver is not None:
                    if isinstance(param_resolver, dict):
                        symbol_names = list(param_resolver.keys())
                        symbol_values = [list(param_resolver.values())]
                expectation_layer = tfq.layers.Expectation()
                expectation = expectation_layer(inputs, symbol_names=symbol_names, symbol_values=symbol_values, operators=observable)
                return {"backend": "cirq_tfq", "expectation": expectation.numpy(), "raw": expectation}
            else:
                # Use cirq simulator
                simulator_instance = cirq.Simulator()
                logger.info("Running circuit on Cirq Simulator (repetitions=%s)...", kwargs.get("repetitions", 1024))
                reps = kwargs.get("repetitions", 1024)
                result = simulator_instance.run(circuit, repetitions=reps)
                return {"backend": "cirq_simulator", "result": result, "raw": result}
        except Exception as e:
            logger.exception("Cirq execution failed: %s", e)
            return {"error": "cirq_run_failed", "detail": str(e)}

    # --------------------------
    # Utilities: unify different outputs
    # --------------------------
    def unify_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map different backend outputs to a common schema for downstream FPT processing.
        Schema:
        {
            "backend": str,
            "type": "qubo" | "counts" | "expectation",
            "payload": {...},  # normalized
            "raw": <backend raw>
        }
        """
        if not isinstance(result, dict):
            return {"backend": "unknown", "type": "raw", "payload": result, "raw": result}

        backend = result.get("backend", "unknown")
        unified = {"backend": backend, "type": "raw", "payload": None, "raw": result.get("raw", result)}

        # QUBO-like
        if backend and backend.startswith("dwave"):
            unified["type"] = "qubo"
            unified["payload"] = {
                "best_sample": result.get("best_sample"),
                "energy": result.get("energy")
            }
            return unified

        if backend and backend.startswith("qiskit"):
            unified["type"] = "counts"
            unified["payload"] = {"counts": result.get("counts") or getattr(result.get("raw", {}), "get_counts", lambda: None)()}
            return unified

        if backend and backend.startswith("cirq"):
            # TFQ expectation
            if "expectation" in result:
                unified["type"] = "expectation"
                unified["payload"] = {"expectation": result["expectation"]}
                return unified
            unified["type"] = "counts"
            unified["payload"] = {"result": result.get("result")}
            return unified

        # Fallback
        unified["payload"] = {"info": result}
        return unified


# --------------------------
# Example helper functions
# --------------------------
def example_qubo_run(bridge: QuantumBridge):
    """
    Example that builds a tiny QUBO and attempts D-Wave hybrid solve (falls back gracefully).
    """
    # Small QUBO: minimize x + y - 2xy
    qubo = {('x', 'x'): 1.0, ('y', 'y'): 1.0, ('x', 'y'): -2.0}
    if dimod is not None:
        try:
            bqm = dimod.BinaryQuadraticModel.from_qubo({('x','x'):1.0, ('y','y'):1.0, ('x','y'):-2.0})
        except Exception:
            bqm = qubo
    else:
        bqm = qubo

    res = bridge.solve_qubo(bqm, backend="dwave_hybrid", time_limit=5)
    print("QUBO result:", bridge.unify_results(res))


def example_qiskit_run(bridge: QuantumBridge):
    """
    Example Qiskit run; uses local simulator if IBM runtime not configured.
    """
    if QuantumCircuit is None:
        print("Qiskit not available in this environment.")
        return
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    res = bridge.run_qiskit(qc, backend="simulator", shots=1024)
    print("Qiskit result:", bridge.unify_results(res))


def example_cirq_run(bridge: QuantumBridge):
    """
    Example Cirq run; uses local simulator (or TFQ if requested and available).
    """
    if cirq is None:
        print("Cirq not available in this environment.")
        return
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CX(q0, q1), cirq.measure(q0, q1))
    res = bridge.run_cirq(circuit, repetitions=1024, simulator="default")
    print("Cirq result:", bridge.unify_results(res))


# --------------------------
# Example usage (script mode)
# --------------------------
if __name__ == "__main__":
    # Example config: replace with your tokens & profiles
    config = {
        "dwave": {"profile": "default", "endpoint": "https://na-west-1.cloud.dwavesys.com/sapi", "token": "<DWAVE_TOKEN>"},
        "qiskit": {"ibm_token": "<IBM_TOKEN>"},
        "cirq": {"use_tfq": False}
    }

    bridge = QuantumBridge(config=config)

    # Try D-Wave hybrid QUBO
    try:
        example_qubo_run(bridge)
    except Exception as e:
        logger.warning("Example QUBO run failed: %s", e)

    # Try Qiskit
    try:
        example_qiskit_run(bridge)
    except Exception as e:
        logger.warning("Example Qiskit run failed: %s", e)

    # Try Cirq
    try:
        example_cirq_run(bridge)
    except Exception as e:
        logger.warning("Example Cirq run failed: %s", e)