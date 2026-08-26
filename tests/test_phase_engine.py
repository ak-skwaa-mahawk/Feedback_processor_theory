import pytest
import numpy as np
from core.phase_engine import ContinuousFeedbackProcessor

def test_phase_initialization():
    proc = ContinuousFeedbackProcessor(num_nodes=8)
    assert len(proc.phases) == 8
    assert len(proc.omega) == 8

def test_phase_flow_step():
    proc = ContinuousFeedbackProcessor(num_nodes=4, coupling_strength=1.0)
    initial_phases = np.copy(proc.phases)
    updated_phases = proc.step_continuous_flow(dt=0.05)
    assert not np.array_equal(initial_phases, updated_phases)

def test_phase_synchronization():
    # Equal natural frequencies with strong coupling must increase coherence
    freqs = np.ones(6) * 1.0
    proc = ContinuousFeedbackProcessor(num_nodes=6, natural_freqs=freqs, coupling_strength=5.0)
    
    initial_coherence = proc.order_parameter()
    for _ in range(200):
        proc.step_continuous_flow(dt=0.02)
    final_coherence = proc.order_parameter()
    
    assert final_coherence >= initial_coherence
    assert final_coherence > 0.8
