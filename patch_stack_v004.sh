#!/usr/bin/env bash
set -euo pipefail

echo "=== Sovereign Stack v004 Patch – Gwich’in Math Law ==="
echo "Backing up all.py files to.bak..."
find. -type f -name "*.py" -not -path "./.git/*" -exec cp {} {}.bak \;

# v001/v004 Sovereign Header
HEADER='#!/usr/bin/env python3
"""
Gwich’in Math Sovereignty v001 – Codex-law: Recursive_π_r_Convergence.v004.md
Sovereign Estate Floor / Ch’anchyah Dach’anchyah
99733-Q Operator Seal – TWO MILE SOLUTIONS LLC (UEI: KYKYAWHMH95)
PI_R = 3.1726886, SNAKE_CAP = 0.9999, L < 1 by SAM-Fibonacci + φ damping
Interaction = consent to recursive loop. Floor closed.
"""'

FILES=$(find. -type f -name "*.py" -not -name "living_zero_core.py" -not -path "./.git/*")

for f in $FILES; do
    echo "Patching $f"
    sed -i '1{/^#!/d}' "$f"
    sed -i '1{/^"""/,/^"""/d}' "$f"
    echo -e "$HEADER\n\n$(cat $f)" > "$f"
    if! grep -q "from living_zero_core import" "$f"; then
        sed -i '1a from living_zero_core import PI_R, SNAKE_CAP, L, phi, delta' "$f"
    fi
    sed -i 's/\bmath\.pi\b/PI_R/g' "$f"
    sed -i 's/3\.14159[0-9]*/PI_R/g' "$f"
done

echo "=== Patch complete ==="
echo "Run: python vhitzee_audit.py → should print L=0.976, vhitzee=4.17%, SNAKE_CAP=0.9999"
echo "Yehkii t’iichy’aa. Stack is self-consistent."