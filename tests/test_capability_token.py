import os, time
from synara_core.modules.capability_token import mint_capability, verify_capability, revoke_capability, list_active_capabilities, CapTokenError

def setup_module():
    os.environ["CAP_TOKEN_SECRET"] = "dev-secret"

def test_mint_verify_and_expire():
    t = mint_capability(sub="alice", scope="read_summary", digest="0xabc", ttl_s=1, extra={"kind":"codex"})
    p = verify_capability(t)
    assert p["sub"] == "alice"
    time.sleep(1.2)
    try:
        verify_capability(t)
        assert False, "should be expired"
    except CapTokenError as e:
        assert "expired" in str(e)

def test_revocation_and_audit():
    t = mint_capability(sub="bob", scope="read_consented", digest="0xdef", ttl_s=60, extra={"kind":"codex"})
    assert any(c["sub"]=="bob" for c in list_active_capabilities())
    revoke_capability(t, reason="test")
    try:
        verify_capability(t)
        assert False, "should be revoked"
    except CapTokenError as e:
        assert "token_revoked" in str(e)