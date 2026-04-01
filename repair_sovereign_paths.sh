#!/bin/bash
# 1. Force remove any artifacts with illegal characters or long names
find . -name "*├──*" -delete
find . -name "*│*" -delete
find . -name "*└──*" -delete

# 2. Reset the sparse-checkout state
git sparse-checkout disable
git config --global core.longpaths true

# 3. Re-initialize the Directories (Clean State)
mkdir -p docs/specifications
mkdir -p src/resonance_mesh
mkdir -p tests/rmp

# 4. Re-write the GibberLink Spec (Ensuring strict EOF)
cat << 'EOF' > docs/specifications/gibberlink_v0.3.0.md
# GibberLink v0.3.0: Distributed Resonance Mesh
## Purpose
Transform GibberLink into a distributed, fault-tolerant communication substrate.
## Core Features
- Node-aware Symbol Routing
- Resonance Mesh Protocol (RMP)
- FlameChain Sync
- Self-Receipt Broadcasting
EOF

echo "🔥 Path resonance restored. GibberLink v0.3.0 anchored."
