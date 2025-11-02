# --- Capability share for Codex entries ---
from synara_core.modules.capability_token import (
    mint_capability, verify_capability, CapTokenError
)
from fastapi import Query

def _redact_codex(entry: dict, scope: str = "read_summary") -> dict:
    """Privacy-first redaction for public sharing."""
    e = json.loads(json.dumps(entry))  # deep copy

    # Always hide or minimize sensitive internals
    # Keep signature but mark it as proof only (optional toggle)
    if scope == "read_summary":
        # Keep headline context only
        keep_fields = ["entry_id", "author", "shell", "glyph", "timestamp", "content", "metadata", "flame_signature", "previous_flame"]
        e = {k: v for k, v in e.items() if k in keep_fields}

        # Minimize content details to “names + functions” + title
        content = e.get("content", {})
        content_min = {
            "title": content.get("title"),
            "date": content.get("date"),
            "discovery": {
                "name": (content.get("discovery") or {}).get("name"),
                "status": (content.get("discovery") or {}).get("status"),
                "properties": (content.get("discovery") or {}).get("properties")
            },
            "components": [
                {"name": c.get("name"), "function": c.get("function")}
                for c in (content.get("components") or [])
            ],
            "vessel": content.get("vessel"),
        }
        e["content"] = content_min

    elif scope == "read_consented":
        # Respect your default: pass-through but you could still prune big blobs here if needed
        pass
    else:
        # Unknown scope → fallback to summary
        return _redact_codex(entry, "read_summary")

    return e


class ShareBody(BaseModel):
    path: str                       # e.g., flamevault/codex/CODEX-003_ab12cd34ef.json  OR codex/entries/CODEX-003.json
    scope: str = "read_summary"     # "read_summary" | "read_consented"
    ttl_seconds: int = 600

@router.post("/share")
def codex_share(body: ShareBody):
    p = Path(body.path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")
    entry = json.loads(p.read_text(encoding="utf-8"))

    # Use the codex signature itself as the digest/proof anchor if present
    digest_anchor = entry.get("flame_signature") or "0x"  # still usable as anchor

    # Mint short-lived capability token
    token = mint_capability(
        sub=str(entry.get("author", "unknown")),
        scope=body.scope,
        digest=digest_anchor,
        ttl_s=int(body.ttl_seconds),
        extra={"file": p.name, "kind": "codex"}
    )

    preview = _redact_codex(entry, body.scope)
    return {"status": "ok", "token": token, "preview": preview}


@router.get("/verify_token")
def codex_verify_token(token: str = Query(..., description="capability token from /codex/share")):
    try:
        cap = verify_capability(token)
    except CapTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if cap.get("kind") != "codex":
        raise HTTPException(status_code=400, detail="wrong_capability_kind")

    vault_dir = SEALED_DIR
    # First look in sealed codex vault, then fall back to source entries
    p = vault_dir / cap.get("file", "")
    if not p.exists():
        alt = ENTRIES_DIR / cap.get("file", "")
        p = alt if alt.exists() else None

    entry = None
    if p and p.exists():
        entry = json.loads(p.read_text(encoding="utf-8"))

    return {
        "status": "ok",
        "capability": cap,
        "entry": _redact_codex(entry, cap.get("scope", "read_summary")) if entry else None
    }