import os, json, time
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from synara_core.modules.capability_token import (
    revoke_capability, list_active_capabilities,
    verify_capability, mint_capability, CapTokenError, _tokhash
)

# existing router = APIRouter() above…
router = APIRouter()

# --- Revocation & Audit ---
@router.post("/revoke")
def codex_revoke(token: str = Query(..., description="capability token to revoke"),
                 reason: str = Query("manual_revocation")):
    return revoke_capability(token, reason=reason)

@router.get("/cap/active")
def codex_cap_active():
    return {"status": "ok", "capabilities": list_active_capabilities()}

# --- Delegation Chains ---
class DelegateBody(BaseModel):
    parent_token: str
    delegate_to: str
    reduced_scope: str | None = None
    reduced_ttl: int | None = None

@router.post("/delegate")
def codex_delegate(body: DelegateBody):
    try:
        parent = verify_capability(body.parent_token)
    except CapTokenError as e:
        raise HTTPException(status_code=401, detail=f"invalid_parent_token:{e}")

    order = ["read_summary", "read_consented", "full_access"]
    parent_scope = parent.get("scope", "read_summary")
    if parent_scope not in order:
        raise HTTPException(400, "unknown_parent_scope")

    new_scope = body.reduced_scope or parent_scope
    if new_scope not in order:
        raise HTTPException(400, "unknown_new_scope")
    if order.index(new_scope) > order.index(parent_scope):
        raise HTTPException(403, "cannot_escalate_privileges")

    now = int(time.time())
    parent_ttl = max(0, int(parent.get("exp", 0)) - now)
    if parent_ttl <= 0:
        raise HTTPException(401, "parent_expired")
    ttl = min(int(body.reduced_ttl or parent_ttl), parent_ttl)

    delegated = mint_capability(
        sub=body.delegate_to,
        scope=new_scope,
        digest=parent.get("digest", "0x"),
        ttl_s=ttl,
        extra={
            "kind": parent.get("extra", {}).get("kind", "codex"),
            "file": parent.get("extra", {}).get("file"),
            "delegated_from": parent.get("sub"),
        },
        parent=_tokhash(body.parent_token)[:16],
    )
    return {
        "status": "delegated",
        "token": delegated,
        "scope": new_scope,
        "expires_in": ttl,
        "chain": [parent.get("sub"), body.delegate_to]
    }
# Still in services/api/codex.py
from pathlib import Path
from synara_core.modules.resonance_policy import (
    ResonancePolicy, WhisperReceipt, mint_resonance_capability_v2
)
from pydantic import BaseModel

POLICY_PATH = os.getenv("RESONANCE_POLICY_PATH", "resonance/policy.yaml")
_resonance_policy = ResonancePolicy(POLICY_PATH if Path(POLICY_PATH).exists() else None)

class ResonanceShareV2Body(BaseModel):
    path: str
    requester: str
    collection: str = "codex"
    score: float | None = None
    cited_flames: list[str] = []
    whisper_receipt: dict | None = None
    context: dict | None = None
    override_base_ttl: int | None = None
    override_max_ttl: int | None = None

@router.post("/resonance_share/v2")
def codex_resonance_share_v2(body: ResonanceShareV2Body):
    p = Path(body.path)
    if not p.exists():
        candidates = [Path("flamevault/codex")/p.name, Path("codex")/p.name, p]
        p = next((c for c in candidates if c.exists()), None)
    if not p or not p.exists():
        raise HTTPException(404, "entry_not_found")

    entry = json.loads(p.read_text(encoding="utf-8"))
    digest_anchor = entry.get("flame_signature") or entry.get("seals", {}).get("self_hash") or "0x"

    score = float(body.score if body.score is not None else 0.5)  # plug in your scorer if desired

    try:
        result = mint_resonance_capability_v2(
            requester=body.requester,
            digest=digest_anchor,
            collection=body.collection,
            score=score,
            policy=_resonance_policy,
            file_name=p.name,
            whisper_receipt=body.whisper_receipt,
            cited_flames=body.cited_flames if body.cited_flames else None,
            extra={"source_path": str(p)}
        )
    except ValueError as e:
        raise HTTPException(403, str(e))

    # minimal preview: you already have _redact_codex; keep using it if present
    preview = entry if result["scope"] == "full_access" else {"title": entry.get("title"), "flame_signature": digest_anchor}
    result["preview"] = preview
    return {"status": "ok", **result}

@router.post("/whisper/generate")
def generate_whisper_receipt(requester: str):
    import secrets, time
    timestamp = int(time.time())
    nonce = secrets.token_hex(16)
    signature = WhisperReceipt.generate(requester, timestamp, nonce)
    return {"requester": requester, "timestamp": timestamp, "nonce": nonce, "signature": signature, "expires_in": 300}

@router.get("/policy/inspect")
def inspect_policy(collection: str = "default"):
    pol = _resonance_policy.get_policy(collection)
    return {
        "collection": collection,
        "policy": pol,
        "example_scores": {
            0.3: {"scope": _resonance_policy.scope_for_score(0.3, collection), "ttl": _resonance_policy.ttl_for_score(0.3, collection)},
            0.6: {"scope": _resonance_policy.scope_for_score(0.6, collection), "ttl": _resonance_policy.ttl_for_score(0.6, collection)},
            0.9: {"scope": _resonance_policy.scope_for_score(0.9, collection), "ttl": _resonance_policy.ttl_for_score(0.9, collection)}
        }
    }