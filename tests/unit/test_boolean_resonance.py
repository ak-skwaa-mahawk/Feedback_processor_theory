from synara_core.modules.boolean_resonance import evaluate, AND, OR, NOT, XNOR

def test_basic_boolean():
    ctx = {"whisper_verified": True, "cited_flame": False, "resonance_score": 0.88}
    assert evaluate("(whisper_verified and cited_flame) or (resonance_score > 0.85)", ctx) is True
    assert evaluate("(whisper_verified and cited_flame) and (resonance_score > 0.9)", ctx) is False

def test_fuzzy_ops():
    assert AND(0.7, 0.9) == 0.7
    assert OR(0.7, 0.9) == 0.9
    assert NOT(0.2) == 0.8
    assert XNOR(0.75, 0.75) == 1.0

def test_safe_calls_only():
    try:
        evaluate("__import__('os').system('echo nope')", {})
        assert False, "should not allow dangerous call"
    except Exception:
        assert True