import pytest
import numpy as np
from core.harmonic_scaling import HarmonicScaleFeedback, PHI

def test_scale_initialization():
    scaler = HarmonicScaleFeedback(num_scales=5, base_freq=1.0)
    assert len(scaler.scale_frequencies) == 5
    assert np.isclose(scaler.scale_frequencies[1], PHI)
    assert np.isclose(scaler.scale_frequencies[2], PHI ** 2)

def test_field_evolution():
    scaler = HarmonicScaleFeedback(num_scales=4)
    init_phases = np.copy(scaler.scale_phases)
    new_phases = scaler.evolve_field(dt=0.05, feedback_drive=0.2)
    assert not np.array_equal(init_phases, new_phases)

def test_field_superposition_bounded():
    scaler = HarmonicScaleFeedback(num_scales=6)
    scaler.evolve_field(dt=0.1)
    superposition = scaler.compute_field_superposition()
    assert isinstance(superposition, complex)
    assert np.abs(superposition) > 0.0
