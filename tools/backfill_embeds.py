import sys, json
from pathlib import Path
from synara_core.modules.self_embed import bump_codex_entry

base = Path(sys.argv[1] if len(sys.argv)>1 else "codex")
for p in base.rglob("*.json"):
    try:
        entry = json.loads(p.read_text(encoding="utf-8"))
        res = bump_codex_entry(entry=entry, file_path=str(p), reason="backfill", actor="cli", scope="full_access")
        print("[EMBED]", p, res["id"])
    except Exception as e:
        print("[SKIP]", p, e)