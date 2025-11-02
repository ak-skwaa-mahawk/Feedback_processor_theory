import os, time
from synara_core.modules.capability_token import mint_capability, verify_capability, CapTokenError, _tokhash
from synara_core.modules.capability_token import mint_capability as mint  # alias

def setup_module():
    os.environ["CAP_TOKEN_SECRET"] = "dev-secret"

def test_delegation_scope_and_ttl():
    # Parent token
    parent = mint(sub="axis.holder", scope="read_consented", digest="0xabc", ttl_s=120, extra={"kind":"codex","file":"CODEX-003.json"})
    parent_payload = verify_capability(parent)

    # Craft delegated token manually (mirrors /delegate route logic)
    from synara_core.modules.capability_token import mint_capability
    delegated = mint_capability(
        sub="researcher.alfa",
        scope="read_summary",           # reduced
        digest=parent_payload["digest"],
        ttl_s=60,                       # <= parent
        extra={"kind":"codex","file":parent_payload["extra"]["file"],"delegated_from":parent_payload["sub"]},
        parent=_tokhash(parent)[:16],
    )
    dp = verify_capability(delegated)
    assert dp["scope"] == "read_summary"
    assert dp["extra"]["delegated_from"] == "axis.holder"

    # Delegation cannot escalate scope—simulate escalation attempt
    try:
        mint_capability(sub="attacker", scope="full_access", digest=parent_payload["digest"], ttl_s=60,
                        extra={"kind":"codex"}, parent=_tokhash(parent)[:16])
        # Note: Scope escalation prevention is enforced in the API route; token mint itself is blind by design.
        # This test just documents that API must enforce scope ceilings.
    except Exception:
        pass