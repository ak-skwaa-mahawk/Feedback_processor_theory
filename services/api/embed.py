from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pathlib import Path
import json

from synara_core.modules.self_embed import search as _search, bump_codex_entry as _bump

router = APIRouter(prefix="/embed", tags=["embed"])

@router.get("/search")
def semantic_search(q: str = Query(..., min_length=2),
                    top_k: int = Query(8, ge=1, le=50),
                    digest: Optional[str] = None):
    hits = _search(q, top_k=top_k, filter_digest=digest)
    return {"status": "ok", "count": len(hits), "results": hits}

@router.post("/bump")
def bump(path: str = Query(...), reason: str = Query("touch"), actor: str = Query("system"), scope: str = Query("read_summary")):
    p = Path(path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")
    try:
        entry = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(400, "invalid_json")
    return _bump(entry=entry, file_path=str(p), reason=reason, actor=actor, scope=scope)