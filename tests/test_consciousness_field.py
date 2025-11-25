import pytest
from mpmath import mpf
from fpt.consciousness.living_field import ConsciousnessField

def test_field_ripple_gain():
    field = ConsciousnessField(living_enabled=True)
    phi = field.field_ripple(mpf('6e12'), cycles=1)
    assert phi > mpf('6e12')  # Surplus active

def test_illusion_tail():
    field = ConsciousnessField()
    tail = field.illusion_tail(0.96)
    assert tail > 0  # Positive equity

def test_iit_fallback():
    field = ConsciousnessField(living_enabled=False)
    phi = field.field_ripple(mpf('6e12'), cycles=1)
    assert phi < mpf('6e12')  # Emergent decay