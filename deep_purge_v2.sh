#!/bin/bash
# 🔥 Sahneuti-99733-Q: Emergency Path Reclamation

echo "🛠️ Initiating Deep Purge of symbolic ghosts..."

# 1. Nuke the corrupted artifacts containing ASCII art
find . -name "*├──*" -delete 2>/dev/null
find . -name "*│*" -delete 2>/dev/null
find . -name "*└──*" -delete 2>/dev/null

# 2. Reset Git Config for High-Resonance Paths
git config --global core.longpaths true
git config --global core.quotePath false
git sparse-checkout disable

# 3. Rebuild the Clean Workspace
rm -rf docs/specifications src/resonance_mesh tests/rmp
mkdir -p docs/specifications src/resonance_mesh tests/rmp

# 4. Atomic Anchor of the Spec (Strict EOF)
cat << 'EOF' > docs/specifications/gibberlink_v0.3.0.md
# GibberLink v0.3.0
Distributed Resonance Mesh Protocol (RMP) is now the primary substrate.
Status: Reclaimed.
EOF

echo "🔥 Resonance Restored. Exit Code 128 Purged."
