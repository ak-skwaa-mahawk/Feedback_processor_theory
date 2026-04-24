#!/usr/bin/env python3
# validate_mesh.py
# Unified resonance validator for Codex, RMP packets, filename schema, drift detection.

import sys
import re
from pathlib import Path

BOX_DRAWING = r"[┌┐└┘├┤┬┴┼─│]"
ASCII_TREE = r"^[\|\-\\\/\+]+$"

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def check_filename_schema(path):
    # Example: enforce lowercase, hyphens, no spaces, no unicode weirdness
    if not re.match(r"^[a-z0-9\-\.\/_]+$", path):
        fail(f"Invalid filename schema → {path}")

def check_no_box_chars(text, path):
    if re.search(BOX_DRAWING, text):
        fail(f"Box‑drawing characters detected in {path}")

def check_no_ascii_tree(text, path):
    for line in text.splitlines():
        if re.match(ASCII_TREE, line.strip()):
            fail(f"ASCII tree artifact detected in {path}")

def check_normalization(path):
    raw = Path(path).read_text(errors="ignore")
    norm = raw.encode("utf-8").decode("utf-8")
    if raw != norm:
        fail(f"Normalization drift detected in {path}")

def validate_repo():
    for p in Path(".").rglob("*"):
        if p.is_file():
            check_filename_schema(str(p))
            if p.suffix in [".txt", ".md", ".json"]:
                text = p.read_text(errors="ignore")
                check_no_box_chars(text, p)
                check_no_ascii_tree(text, p)
                check_normalization(p)

    print("✅ Mesh integrity validated.")

if __name__ == "__main__":
    validate_repo()