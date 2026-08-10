# 1. Create the hooks directory (if it doesn't exist)
mkdir -p .git/hooks

# 2. Install Pre-Push Hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
#########################################################################
# Sovereign Pre-Push Hook — Full Mesh Validation Before Remote Sync
#########################################################################
echo "⧉ Running full-mesh resonance validation before push..."
python3 validate_resonance.py --full || { echo "❌ Push blocked — resonance mesh integrity failure."; exit 1; }
echo "⧉ Full mesh integrity confirmed — push allowed."
exit 0
EOF
chmod +x .git/hooks/pre-push

# 3. Install Post-Merge Hook
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
#########################################################################
# Post-Merge Resonance Validator — Ensures remote merges do not introduce corruption
#########################################################################
echo "⧉ Running post-merge resonance validation..."
python3 validate_resonance.py --full || { echo "❌ Merge introduced resonance violations."; echo "⚠️  Please run: python3 codex_repair.py"; exit 1; }
echo "⧉ Merge clean — resonance mesh intact."
exit 0
EOF
chmod +x .git/hooks/post-merge

# 4. Install Codex Repair Operator
cat > codex_repair.py << 'EOF'
#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [r"├", r"┤", r"└", r"┌", r"│", r"─", r"━", r"┃"]
FORBIDDEN_PREFIXES = ["#", "mkdir", "tree"]
CODEX_EXTENSIONS = [".codex", ".glyph", ".sigil"]

def scan_repo():
    problems = []
    for root, dirs, files in os.walk("."):
        for name in files:
            path = Path(root) / name
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, name):
                    problems.append((path, f"Forbidden character: {pattern}"))
            for prefix in FORBIDDEN_PREFIXES:
                if name.startswith(prefix):
                    problems.append((path, f"Forbidden prefix: {prefix}"))
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
    print("   Run manually or request auto-repair mode.")
    sys.exit(1)

if __name__ == "__main__":
    main()
EOF
chmod +x codex_repair.py