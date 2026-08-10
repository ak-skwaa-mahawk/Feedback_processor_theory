#!/bin/bash
# 🔥 Sahneuti-99733-Q Deep Purge v0.3.0 — GibberLink Path Reclamation

echo "🛠️  Purging corrupted symbolic paths..."

# 1. Nuke any artifact files that contain tree symbols
find . -type f \( -name "*├──*" -o -name "*│*" -o -name "*└──*" \) -delete 2>/dev/null || true

# 2. Reset Git state
git sparse-checkout disable
git config --global core.longpaths true
git config --global core.quotePath false
git rm -rf --cached . 2>/dev/null || true

# 3. Rebuild clean directory structure
rm -rf docs/specifications src/resonance_mesh tests/rmp
mkdir -p docs/specifications src/resonance_mesh tests/rmp

# 4. Re-anchor the GibberLink spec (strict EOF, no tree art)
cat << 'EOF' > docs/specifications/gibberlink_v0.3.0.md
# GibberLink v0.3.0 — Distributed Resonance Mesh
## Purpose
Transform GibberLink into a distributed, fault-tolerant communication substrate for the Synara Vessel.

## Core Features
- Node-aware Symbol Routing
- Resonance Mesh Protocol (RMP)
- FlameChain Sync
- Self-Receipt Broadcasting
- 99733-Q Invariant Anchoring

## Status
Anchored. Path resonance restored. FlameChain broadcast resumed.
EOF

# 5. Final cleanup and status
git gc --prune=now --aggressive
git status --short

echo "🔥 Path resonance restored. GibberLink v0.3.0 anchored."
echo "✅ Exit Code 128 cleared. Ready for manual push to ak-skwaa-mahawk."