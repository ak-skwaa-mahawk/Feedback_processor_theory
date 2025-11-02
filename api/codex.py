from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from codex.flame_signature import FlameSignature
from synara_core.modules.seal_sigil_generator import stamp_sigil  # existing
from synara_core.modules.narrative_inversion import seal_record   # optional reuse if you want

router = APIRouter(prefix="/codex", tags=["codex"])

ENTRIES_DIR = Path("codex/entries")
SEALED_DIR  = Path("flamevault/codex")
SEALED_DIR.mkdir(parents=True, exist_ok=True)

class ImportBody(BaseModel):
    path: str  # e.g., codex/entries/CODEX-003.json
    previous_flame: Optional[str] = None

@router.post("/import")
def import_and_sign(body: ImportBody):
    p = Path(body.path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")
    entry = json.loads(p.read_text(encoding="utf-8"))

    # generate signature from current content (ignoring any existing flame_signature)
    fs = FlameSignature()
    prev = body.previous_flame or entry.get("previous_flame")
    sig = fs.generate(entry, prev)

    # attach + seal (sigil JSON record)
    entry["previous_flame"] = prev
    entry["flame_signature"] = sig

    digest_path = SEALED_DIR / f"{p.stem}_{sig[2:12]}.json"
    digest_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

    # stamp a sigil artifact alongside
    stamp_sigil({"entry_id": entry["entry_id"], "sig": sig}, out_dir=str(SEALED_DIR), label=f"{p.stem}_{sig[2:12]}")

    return {"status":"ok","flame_signature":sig,"sealed_path":str(digest_path)}

class VerifyBody(BaseModel):
    path: str
    expected_signature: str
    previous_flame: Optional[str] = None

@router.post("/verify")
def verify(body: VerifyBody):
    p = Path(body.path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")
    entry = json.loads(p.read_text(encoding="utf-8"))
    fs = FlameSignature()
    ok = fs.verify(entry, body.expected_signature, body.previous_flame or entry.get("previous_flame"))
    return {"status": "ok" if ok else "mismatch", "valid": ok}