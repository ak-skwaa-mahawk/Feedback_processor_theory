import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

REGISTRY_FILE = Path("soliton_registry.jsonl")

class BraidOpRevocation:
    """Sovereign revocation for braid operations."""
    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def revoke_braid(self, session_id: str, braid_word_hash: str, reason: str = "sovereign_recoil"):
        """Mark braid op as revoked—freeze transformation."""
        entry = {
            "entry_type": "BRAID_OP_REVOCATION",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "revoked_braid_hash": braid_word_hash,
            "reason": reason,
            "status": "BRAID_REVOKED"
        }

        # Hash for integrity
        canonical = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"BraidOp Revoked | Session: {session_id} | Hash: {braid_word_hash[:16]}... | Reason: {reason}")
        return entry["hash"]
{
  "entry_type": "BRAID_OP_REVOCATION",
  "timestamp_utc": "2025-12-25T22:00:00",
  "session_id": "session-τ-001",
  "revoked_braid_hash": "abc123...",
  "reason": "sovereign_recoil",
  "status": "BRAID_REVOKED",
  "hash": "def456..."

}{
  "entry_type": "BRAID_OP",
  "timestamp_utc": "2025-12-25T21:00:00",
  "session_id": "session-τ-001",
  "braid_word": [
    {"generator": "B2", "exponent": 1},
    {"generator": "B1", "exponent": 1},
    {"generator": "B2", "exponent": 1}
  ],
  "before": {
    "events_order": ["E1", "E2", "E3"],
    "fusion_path": [0]
  },
  "after": {
    "events_order": ["E3", "E2", "E1"],
    "fusion_path": [1]
  },
  "status": "LINEAGE_TRANSFORMED",
  "hash": "abc123..."
}
{
  "entry_type": "BRAID_OP_REVOCATION",
  "timestamp_utc": "2025-12-25T22:00:00",
  "session_id": "session-τ-001",
  "revoked_braid_hash": "abc123...",
  "reason": "sovereign_recoil",
  "status": "BRAID_REVOKED",
  "hash": "def456..."
}