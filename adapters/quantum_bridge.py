"""
quantum_bridge.py

Unified Quantum Bridge for FPT-Ω
Supports:
 - D-Wave Leap (dwave-system / LeapHybridSampler)
 - IBM Qiskit (qiskit / qiskit_ibm_runtime)
 - Google Cirq + TFQ (cirq, tensorflow-quantum)

Design:
 - Safe fallbacks if SDKs are not installed (mock responses)
 - Normalizes outputs into a single 'resonance_score' ∈ [0, 1]
 - Minimal dependencies required to run in test mode

Usage:
  from quantum_bridge import unified_resonance_assessment, solve_dwave_qubo
  result = unified_resonance_assessment(...)
  print(result['resonance_score'], result['raw'])

Auth / Environment:
 - D-Wave: configure profile with `dwave config create` or set env DWAVE_PROFILE
 - IBM: set IBM token via QiskitRuntimeService.save_account(), or set env IBM_TOKEN
 - Cirq / TFQ: requires tensorflow & tfq - otherwise fallback mocked behavior

Author: John B. Carroll Jr. (ak-skwaa-mahawk)
© Two Mile Solutions LLC — 2025
"""
import os
import math
import time
import random

# ---------- Optional imports (wrapped) ----------
# D-Wave
try:
    from dwave.system import LeapHybridSampler, DWaveSampler, EmbeddingComposite
    DWAVE_AVAILABLE = True
except Exception:
    LeapHybridSampler = None
    DWaveSampler = None
    EmbeddingComposite = None
    DWAVE_AVAILABLE = False

# Qiskit
try:
    from qiskit import QuantumCircuit, Aer, execute
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
    QISKIT_AVAILABLE = True
except Exception:
    QuantumCircuit = None
    Aer = None
    execute = None
    QiskitRuntimeService = None
    Sampler = None
    QISKIT_AVAILABLE = False

# Cirq + TFQ
try:
    import cirq
    import sympy
    import numpy as np
    import tensorflow as tf
    import tensorflow_quantum as tfq
    CIRQ_AVAILABLE = True
except Exception:
    cirq = None
    sympy = None
    np = None
    tf = None
    tfq = None
    CIRQ_AVAILABLE = False

# dimod (for building BQM if user wants)
try:
    from dimod import BinaryQuadraticModel
    DIMOD_AVAILABLE = True
except Exception:
    BinaryQuadraticModel = None
    DIMOD_AVAILABLE = False

# ---------- Utilities ----------
def _normalize_energy_to_score(energy, energy_bounds=(-100.0, 100.0)):
    """
    Map an energy (possibly negative) to a 0..1 resonance score.
    Lower energy (better optimization) → higher score.
    energy_bounds: (min_energy, max_energy) used for normalization.
    Clamped to [0,1].
    """
    min_e, max_e = energy_bounds
    # invert so that lower energy = higher score
    # if energy <= min_e => score=1.0; energy >= max_e => score=0.0
    if math.isfinite(energy):
        score = (max_e - energy) / (max_e - min_e)
    else:
        score = 0.0
    return max(0.0, min(1.0, score))

def _mock_dwave_solution():
    # returns a plausible mock sample and mock energy
    sample = {'π': 1, 'ε': 1}
    energy = random.uniform(-5.0, 5.0)
    return sample, energy

def _mock_qiskit_counts():
    return {'00': 512, '11': 512}

def _mock_cirq_expectation():
    # returns expectation between -1 and 1
    return random.uniform(-0.9, 0.9)

# ---------- D-Wave wrapper ----------
def solve_dwave_qubo(bqm, time_limit=5, profile="default", use_hybrid=True, **kwargs):
    """
    Solve a BinaryQuadraticModel (dimod) using D-Wave Leap (hybrid recommended).
    - bqm: a dimod.BinaryQuadraticModel instance OR a dict-like QUBO
    - time_limit: seconds for hybrid sampler
    - use_hybrid: if True, uses LeapHybridSampler; else attempts pure quantum annealer
    Returns: dict { 'sample': {...}, 'energy': float, 'meta': {...} }
    """
    if not DWAVE_AVAILABLE:
        sample, energy = _mock_dwave_solution()
        return {'sample': sample, 'energy': energy, 'meta': {'mock': True}}

    # Real path
    try:
        if use_hybrid:
            sampler = LeapHybridSampler(profile=profile)
            # sampler.sample accepts dimod BQM directly
            sampleset = sampler.sample(bqm, time_limit=time_limit, **kwargs)
            best = sampleset.first
            return {'sample': dict(best.sample), 'energy': float(best.energy), 'meta': {'sampler': 'hybrid'}}
        else:
            sampler = EmbeddingComposite(DWaveSampler(profile=profile))
            sampleset = sampler.sample(bqm, num_reads=1000, **kwargs)
            best = sampleset.first
            return {'sample': dict(best.sample), 'energy': float(best.energy), 'meta': {'sampler': 'annealer'}}
    except Exception as exc:
        # fallback to mock
        sample, energy = _mock_dwave_solution()
        return {'sample': sample, 'energy': energy, 'meta': {'mock': True, 'error': str(exc)}}

# ---------- Qiskit wrapper ----------
def run_qiskit_circuit(qc, backend_name=None, shots=1024, use_statevector=False, profile=None):
    """
    Execute a