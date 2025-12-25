import json
from pathlib import Path
from typing import Dict, List, Any

REGISTRY_FILE = Path("soliton_registry.jsonl")

class BraidOpEngine:
    """
    Sovereign engine for:
    - storing braid ops
    - storing revocations
    - resolving lineage with revocation applied
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load all registry entries."""
        if not self.path.exists():
            return []
        with self.path.open() as f:
            return [json.loads(line) for line in f]

    def get_lineage(self, session_id: str) -> Dict[str, Any]:
        """
        Resolve lineage for a session:
        - apply braid ops in order
        - ignore revoked braid ops
        - return final lineage state
        """
        entries = self._load_entries()

        # Filter for this session
        ops = [e for e in entries if e.get("session_id") == session_id]

        # Track revoked braid hashes
        revoked = {
            e["revoked_braid_hash"]
            for e in ops
            if e["entry_type"] == "BRAID_OP_REVOCATION"
        }

        # Active braid ops
        active_ops = [
            e for e in ops
            if e["entry_type"] == "BRAID_OP" and e["hash"] not in revoked
        ]

        if not active_ops:
            return {}

        # Apply in chronological order
        active_ops.sort(key=lambda e: e["timestamp_utc"])

        # Final state after last active braid
        final = active_ops[-1]["after"]

        return final

    def is_revoked(self, braid_hash: str) -> bool:
        """Check if a braid op is revoked."""
        entries = self._load_entries()
        return any(
            e.get("revoked_braid_hash") == braid_hash
            for e in entries
            if e["entry_type"] == "BRAID_OP_REVOCATION"
        )