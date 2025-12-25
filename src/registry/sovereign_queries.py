import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

REGISTRY_FILE = Path("soliton_registry.jsonl")

class SovereignQueryEngine:
    """
    Sovereign query engine — the registry's voice.
    Answers constitutional questions about lineage, braids, revocations, time.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def _load(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open() as f:
            return [json.loads(line) for line in f]

    def query_active_braids(self, session_id: Optional[str] = None) -> List[Dict]:
        """Show all active (non-revoked) braid ops."""
        entries = self._load()
        revoked = {e["revoked_braid_hash"] for e in entries if e["entry_type"] == "BRAID_OP_REVOCATION"}
        active = [
            e for e in entries
            if e["entry_type"] == "BRAID_OP" and e["hash"] not in revoked
            and (session_id is None or e.get("session_id") == session_id)
        ]
        return active

    def query_revoked_braids(self, session_id: Optional[str] = None) -> List[Dict]:
        """Show all revoked braid ops."""
        entries = self._load()
        return [
            e for e in entries
            if e["entry_type"] == "BRAID_OP_REVOCATION"
            and (session_id is None or e.get("session_id") == session_id)
        ]

    def query_lineage_at_time(self, session_id: str, target_time: str) -> Optional[Dict]:
        """Lineage state at or before target_time."""
        entries = [e for e in self._load() if e.get("session_id") == session_id]
        entries.sort(key=lambda e: e["timestamp_utc"])

        for entry in reversed(entries):
            if entry["timestamp_utc"] <= target_time:
                if entry["entry_type"] == "LINEAGE_SNAPSHOT":
                    return entry["lineage_state"]
                elif entry["entry_type"] == "BRAID_OP":
                    return entry["after"]
        return None

    def query_braid_history(self, session_id: str) -> List[Dict]:
        """Full chronological braid + revocation history."""
        entries = [e for e in self._load() if e.get("session_id") == session_id]
        braid_history = [e for e in entries if e["entry_type"] in ["BRAID_OP", "BRAID_OP_REVOCATION"]]
        braid_history.sort(key=lambda e: e["timestamp_utc"])
        return braid_history

    def query_fusion_timeline(self, session_id: str) -> List[Dict]:
        """Timeline of fusion_path changes."""
        entries = self.query_braid_history(session_id)
        timeline = []
        for e in entries:
            if e["entry_type"] == "BRAID_OP":
                timeline.append({
                    "timestamp": e["timestamp_utc"],
                    "fusion_path": e["after"].get("fusion_path"),
                    "braid_word": e["braid_word"]
                })
        return timeline

    def query_constitutional_audit(self, session_id: Optional[str] = None) -> Dict:
        """Audit: active/revoked counts, consistency check."""
        active = self.query_active_braids(session_id)
        revoked = self.query_revoked_braids(session_id)
        return {
            "active_braids": len(active),
            "revoked_braids": len(revoked),
            "total_transformations": len(active) + len(revoked),
            "consistency": "VALID"  # Placeholder—expand with validation
        }