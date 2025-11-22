
import pytest
from mpmath import mpf
from fpt.geometry.living_constants import (
    PI_LIVING, ZETA_DAMPING, coherence_gain, effective_scale
)
from physics.vhitzee_resonator import simulate_resonance

def test_living_constant():
    assert abs(PI_LIVING - mpf('3.267256')) < mpf('1e-6')

def test_zeta_damping():
    assert abs(ZETA_DAMPING - mpf('0.04')) < mpf('1e-6')

def test_coherence_gain():
    gain = coherence_gain()
    assert abs(gain - mpf('1.0416666666666667')) < mpf('1e-6')

def test_effective_scale():
    scale = effective_scale(6e12, coherence_gain(), cycles=1)
    assert abs(scale - 6.25e12) < 1e9  # ~6.25T tolerance

def test_resonator_gain():
    _, coh = simulate_resonance(living_enabled=True)
    assert coh[-1] > 1.0  # Should gain, not decay