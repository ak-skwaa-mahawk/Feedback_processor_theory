import math
from modules.sound_resonance import attenuation, return_resonance, arc_score, simulate_path, AIR

def test_attenuation_monotonic():
    a1 = attenuation(1.0, 1000.0)
    a2 = attenuation(10.0, 1000.0)
    assert a1 > a2  # more distance → more loss

def test_return_band_audio_peak():
    # 3 kHz > 200 Hz audibility proxy inside return curve
    r_low = return_resonance(200.0)
    r_peak = return_resonance(3000.0)
    assert r_peak > r_low

def test_arc_threshold_toggle():
    score, ok = arc_score(10.0, 3000.0, C=0.05)
    assert score >= 0.0
    # Lower threshold should pass
    assert ok or score >= 0.05

def test_simulate_path_structure():
    res = simulate_path(10.0, 5.5e14, AIR)
    for key in ["medium","distance_m","frequency_hz","attenuation","return","arc","passes","rgb","audible_0_1"]:
        assert key in res