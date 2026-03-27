from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SACRED_LOG = DATA_DIR / "sacred_log.json"
BACKUPS_DIR = DATA_DIR / "backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

try:
    from synara_core.modules.seal_sigil_generator import stamp_sigil
except Exception:
    stamp_sigil = None

def append_sacred_log(entry: Dict[str, Any]) -> None:
    log = []
    if SACRED_LOG.exists():
        try:
            log = json.loads(SACRED_LOG.read_text(encoding="utf-8"))
        except Exception:
            log = []
    log.append(entry)
    SACRED_LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")

def write_backup(entry: Dict[str, Any]) -> Path:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    path = BACKUPS_DIR / f"fpt_{ts.replace(':', '-')}.json"
    path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def seal_artifacts(label: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    out = {"sealed": False}
    if stamp_sigil:
        record_path = stamp_sigil(payload, out_dir="data", label=label, echo_payload=True, make_qr=True)
        out.update({"sealed": True, "record": str(record_path)})
    return out