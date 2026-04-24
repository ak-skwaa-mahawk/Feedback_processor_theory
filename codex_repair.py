#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    r"├", r"┤", r"└", r"┌", r"│", r"─", r"━", r"┃",
]

FORBIDDEN_PREFIXES = [
    "#", "mkdir", "tree"
]

CODEX_EXTENSIONS = [
    ".codex", ".glyph", ".sigil"
]

def scan_repo():
    problems = []
    for root, dirs, files in os.walk("."):
        for name in files:
            path = Path(root) / name

            # Forbidden characters
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, name):
                    problems.append((path, f"Forbidden character: {pattern}"))

            # Forbidden prefixes
            for prefix in FORBIDDEN_PREFIXES:
                if name.startswith(prefix):
                    problems.append((path, f"Forbidden prefix: {prefix}"))

            # Codex drift
            if path.suffix in CODEX_EXTENSIONS:
                with open(path, "rb") as f:
                    data = f.read()
                    if b"\r\n" in data or b"\n" in data:
                        problems.append((path, "Codex drift (newline detected)"))

    return problems

def main():
    print("⧉ Scanning full repository for resonance violations...\n")

    problems = scan_repo()

    if not problems:
        print("✓ No issues found — mesh is clean.")
        sys.exit(0)

    print("❌ Resonance violations detected:\n")
    for path, issue in problems:
        print(f"  • {path} — {issue}")

    print("\n⚠️ Automatic repair is not applied by default.")
    print("   You may rename or fix files manually, or request an auto‑repair mode.\n")

    sys.exit(1)

if __name__ == "__main__":
    main()