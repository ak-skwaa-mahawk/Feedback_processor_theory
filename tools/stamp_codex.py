#!/usr/bin/env python3
import json, sys, hashlib, base64
from pathlib import Path
from datetime import datetime

def b32_no_padding(hex_digest: str) -> str:
    raw = bytes.fromhex(hex_digest)
    b32 = base64.b32encode(raw).decode('ascii')
    return b32.rstrip('=')

def main(path: str, set_flame: bool = True):
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    # Hash of full text (canonical: as-is file content)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    b32 = b32_no_padding(h)

    data = json.loads(raw)
    ids = data.setdefault("identifiers", {})
    ids["sha256_digest"] = h
    ids["b32_short"] = b32
    ids["handshake_id"] = f"{data.get('code_anchor','FLM-UNKNOWN')}::{h}"
    if set_flame:
        # Flame signature = prefixed digest for public verification (simple mode)
        data["identifiers"]["flame_signature"] = f"0x{h}"

    # Optional: stamp timestamp if templated
    meta = data.setdefault("meta", {})
    if meta.get("created_utc") == "{{UTC_NOW}}":
        meta["created_utc"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    out = json.dumps(data, indent=2, ensure_ascii=False)
    p.write_text(out, encoding="utf-8")

    print("[STAMPED]")
    print("  file        :", str(p))
    print("  sha256      :", h)
    print("  b32_short   :", b32)
    print("  handshake_id:", data["identifiers"]["handshake_id"])
    if set_flame:
        print("  flame_sig   :", data['identifiers']['flame_signature'])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/stamp_codex.py codex/ATTENUATION_THEORY.json")
        sys.exit(1)
    main(sys.argv[1])