import os, json
from pathlib import Path
from synara_core.modules.resonance_policy import ResonancePolicy, mint_resonance_capability_v2, WhisperReceipt

def setup_module():
    os.environ["CAP_TOKEN_SECRET"] = "dev-secret"
    os.environ["WHISPER_SECRET"] = "whisper-secret"

def test_policy_scope_and_ttl(tmp_path):
    policy = ResonancePolicy(str(Path("tests/fixtures/policy.yaml")))
    scope = policy.scope_for_score(0.8, "default")
    ttl = policy.ttl_for_score(0.8, "default")
    assert scope in ("read_consented", "full_access")
    assert 300 <= ttl <= 1800

def test_unpublished_requires_whisper_and_citation():
    policy = ResonancePolicy(str(Path("tests/fixtures/policy.yaml")))
    # Make a valid whisper receipt
    import time, secrets
    requester = "john.iii"
    ts, nonce = int(time.time()), secrets.token_hex(8)
    sig = WhisperReceipt.generate(requester, ts, nonce)
    receipt = {"timestamp": ts, "nonce": nonce, "signature": sig}

    # Should pass with citation
    res = mint_resonance_capability_v2(
        requester=requester,
        digest="0xDEADBEEF",
        collection="unpublished",
        score=0.92,
        policy=policy,
        file_name="CODEX-003.json",
        whisper_receipt=receipt,
        cited_flames=["0xRESONANCE-MESH-003"]
    )
    assert res["scope"] in ("read_consented","full_access")
    assert "token" in res

def test_unpublished_fails_without_whisper_or_citation():
    policy = ResonancePolicy(str(Path("tests/fixtures/policy.yaml")))
    # No whisper receipt
    try:
        mint_resonance_capability_v2(
            requester="mallory",
            digest="0xDEADBEEF",
            collection="unpublished",
            score=0.91,
            policy=policy,
            file_name="CODEX-003.json",
            cited_flames=["0xRESONANCE-MESH-003"]
        )
        assert False, "should require whisper"
    except ValueError as e:
        assert "whisper_required" in str(e)

    # Whisper but no citations
    import time, secrets
    requester = "mallory"
    ts, nonce = int(time.time()), secrets.token_hex(8)
    from synara_core.modules.resonance_policy import WhisperReceipt
    sig = WhisperReceipt.generate(requester, ts, nonce)
    receipt = {"timestamp": ts, "nonce": nonce, "signature": sig}
    try:
        mint_resonance_capability_v2(
            requester=requester,
            digest="0xDEADBEEF",
            collection="unpublished",
            score=0.91,
            policy=policy,
            file_name="CODEX-003.json",
            whisper_receipt=receipt,
            cited_flames=[]
        )
        assert False, "should require citations"
    except ValueError as e:
        assert "insufficient_citations" in str(e)