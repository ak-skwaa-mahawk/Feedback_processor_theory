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