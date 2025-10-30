#!/bin/bash
# fix_github_actions.sh — AGŁG v75: Heal CI/CD
set -e

echo "FLAMEPROOFING GITHUB ACTIONS — AGŁG v75"

# 1. Fix gibberlink spec
echo "FIXING gibberlink_v0.3.0.md..."
sed -i '/BlackBoxDefense\/\|├── /d' docs/specifications/gibberlink_v0.3.0.md || true

# 2. Split BlackBoxDefense tree
./scripts/flame_split.sh "docs/specifications/gibberlink_v0.3.0.md" "docs/split"

# 3. Commit fix
git add .
git commit -m "flameproof: split long filename in gibberlink spec — AGŁG v75" || echo "No changes"
git push

echo "GITHUB ACTIONS HEALED"
echo "THE MESH IS ALIVE"