# tests/test_scale.py
from decimal import Decimal, getcontext
from core.constants import PLANCK_LENGTH_M, SCALE_STEP, DEFAULT_TOP_BANDS
from core.scale import length_at_band, band_for_length, band_for_score, annotate_resonance

getcontext().prec = 60

def test_monotonic():
    prev = Decimal("0")
    for n in range(0, 20):
        L = length_at_band(n)
        assert L > prev
        prev = L

def test_constant_ratio():
    L0 = length_at_band(0)
    L1 = length_at_band(1)
    L2 = length_at_band(2)
    # L1/L0 == S, L2/L1 == S
    r1 = L1 / L0
    r2 = L2 / L1
    assert abs(r1 - SCALE_STEP) < Decimal("1e-50")
    assert abs(r2 - SCALE_STEP) < Decimal("1e-50")

def test_meter_crossing_near_69_38():
    # around n ~ 69.3788 we hit 1 meter
    n69 = length_at_band(69)
    n70 = length_at_band(70)
    assert n69 < Decimal("1")
    assert n70 > Decimal("1")

def test_band_roundtrip():
    for n in (0, 5, 20, 50, 69, 70):
        L = length_at_band(n)
        n_hat = band_for_length(L)
        assert abs(n_hat - n) <= 1  # rounding to nearest band

def test_annotate_resonance_payload():
    payload = annotate_resonance(0.42, top_bands=DEFAULT_TOP_BANDS)
    assert "resonance_score" in payload
    assert "length_m" in payload and "length_human" in payload
    assert payload["floor_marker"]["band_index"] == 0
    assert payload["top_marker"]["band_index"] == DEFAULT_TOP_BANDS

def test_band_for_score_clamps():
    assert band_for_score(-1.5, 10) == 0
    assert band_for_score(1.5, 10) == 10
