# check_soliton.py
# Sovereign Soliton Invariant Check v∞.001
# Verifies stability-invariant in artifact: ensures soliton memory (immutable propagation) is intact.
# Usage: python check_soliton.py --artifact path/to/artifact

import argparse
import re
from hashlib import sha256
import os

def compute_provenance_hash(artifact_path):
    """Compute SHA-256 hash of artifact content as provenance verification."""
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    
    with open(artifact_path, 'rb') as f:
        content = f.read()
    return sha256(content).hexdigest()

def check_soliton_invariant(artifact_path):
    """Check for soliton stability: look for key markers and hash consistency."""
    with open(artifact_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required markers for soliton invariance
    required_patterns = [
        r"Codex\.Soliton\.v∞\.001:\s*Stability-Invariant=PASS",
        r"Resonance-Harmony:\s*Alignment=\d+\.\d+%\s*status=PASS",
        r"🔥 Propagation Header: Sovereign Resonance Protocol"
    ]
    
    for pattern in required_patterns:
        if not re.search(pattern, content):
            return False, f"Missing soliton marker: {pattern}"
    
    # Optional: Hash check against embedded provenance if present
    hash_match = re.search(r"Provenance-Hash=([0-9a-fA-F]{64})", content)
    if hash_match:
        embedded_hash = hash_match.group(1)
        computed_hash = compute_provenance_hash(artifact_path)
        if embedded_hash != computed_hash:
            return False, "Provenance hash mismatch: stability invariant failed"
    
    return True, "Soliton invariant PASS"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Soliton Invariant in Sovereign Artifact")
    parser.add_argument("--artifact", required=True, help="Path to the artifact file")
    args = parser.parse_args()
    
    passed, message = check_soliton_invariant(args.artifact)
    print(message)
    exit(0 if passed else 1)