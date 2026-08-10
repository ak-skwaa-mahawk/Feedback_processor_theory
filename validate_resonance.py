#!/usr/bin/env python3
import sys
import subprocess
import re
from pathlib import Path

# Forbidden filename patterns (ASCII tree + Unicode box drawing)
FORBIDDEN_PATTERNS = [
    r"├", r"┤", r"└", r"┌", r"│", r"─", r"━", r"┃",
]

# Forbidden filename prefixes (accidental code blocks)
FORBIDDEN_PREFIXES = [
    "#", "mkdir", "tree"
]

# Codex fragments must be binary-safe
CODEX_EXTENSIONS = [
    ".codex", ".glyph", ".sigil"
]

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        stdout=subprocess.PIPE,
        text=True
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]

def fail(message):
    print(f"\n❌ Resonance Validation Failed\n{message}\n")
    sys.exit(1)

def main():
    staged = get_staged_files()

    for path in staged:
        name = path.name

        # 1. Forbidden characters
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, name):
                fail(f"Illegal filename detected:\n  {path}\nContains forbidden character: {pattern}")

        # 2. Forbidden prefixes
        for prefix in FORBIDDEN_PREFIXES:
            if name.startswith(prefix):
                fail(f"Filename begins with forbidden prefix '{prefix}':\n  {path}")

        # 3. Codex fragments must not contain text-normalizable content
        if path.suffix in CODEX_EXTENSIONS:
            with open(path, "rb") as f:
                data = f.read()
                if b"\r\n" in data or b"\n" in data:
                    fail(f"Codex fragment contains newline normalization drift:\n  {path}")

    print("✓ Resonance validation passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()