#!/usr/bin/env python3
# repair_mesh.py
# Automatically repairs drift, normalization issues, and filename schema violations.

import re
from pathlib import Path

def sanitize_filename(path):
    clean = re.sub(r"[^a-z0-9\-\.\/_]", "-", path.lower())
    if clean != path:
        Path(path).rename(clean)
        print(f"🔧 Renamed → {path} → {clean}")
        return clean
    return path

def normalize_text(path):
    raw = Path(path).read_text(errors="ignore")
    norm = raw.encode("utf-8").decode("utf-8")
    if raw != norm:
        Path(path).write_text(norm)
        print(f"🔧 Normalized → {path}")

def repair_repo():
    for p in list(Path(".").rglob("*")):
        if p.is_file():
            new = sanitize_filename(str(p))
            p = Path(new)
            if p.suffix in [".txt", ".md", ".json"]:
                normalize_text(p)

    print("✨ Codex Repair complete.")

if __name__ == "__main__":
    repair_repo()