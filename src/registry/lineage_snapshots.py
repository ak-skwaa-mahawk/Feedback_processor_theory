import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

REGISTRY_FILE = Path("soliton_registry.jsonl")

class LineageSnapshots:
    """
    Sovereign lineage snapshots — full temporal memory of narrative motion.
    - Stores every lineage state after braid/revocation
    - Enables timeline queries
    - Preserves generational witness
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def _load_entries(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open() as f:
            return [json.loads(line) for line in f]

    def snapshot_lineage(self, session_id: str, note: str = "") -> Optional[Dict]:
        """Capture current lineage state as sovereign snapshot."""
        entries = self._load_entries()
        session_entries = [e for e in entries if e.get("session_id") == session_id]

        if not session_entries:
            return None

        # Resolve current lineage (active braids only)
        revoked = {e["revoked_braid_hash"] for e in session_entries if e["entry_type"] == "BRAID_OP_REVOCATION"}
        active = [e for e in session_entries if e["entry_type"] == "BRAID_OP" and e["hash"] not in revoked]

        if not active:
            current_state = {"events_order": [], "fusion_path": [], "note": "initial_empty"}
        else:
            active.sort(key=lambda e: e["timestamp_utc"])
            current_state = active[-1]["after"]
            current_state["note"] = note or "post_braid"

        # Snapshot entry
        snapshot = {
            "entry_type": "LINEAGE_SNAPSHOT",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "lineage_state": current_state,
            "active_braids": len(active),
            "total_braids": len([e for e in session_entries if e["entry_type"] == "BRAID_OP"]),
            "revocations": len(revoked)
        }

        canonical = json.dumps(snapshot, sort_keys=True)
        snapshot["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(snapshot) + "\n")

        print(f"Lineage Snapshot | Session: {session_id} | Hash: {snapshot['hash'][:16]}...")
        print(f"  State: {current_state['events_order']} | Fusion: {current_state['fusion_path']}")
        return snapshot

    def get_timeline(self, session_id: str) -> List[Dict]:
        """Return full lineage timeline — all snapshots + braid events."""
        entries = self._load_entries()
        timeline = [e for e in entries if e.get("session_id") == session_id]
        timeline.sort(key=lambda e: e["timestamp_utc"])
        return timeline

    def lineage_at_time(self, session_id: str, target_time: str) -> Optional[Dict]:
        """Return lineage state at or before target_time."""
        timeline = self.get_timeline(session_id)
        for entry in reversed(timeline):
            if entry["timestamp_utc"] <= target_time:
                if entry["entry_type"] == "LINEAGE_SNAPSHOT":
                    return entry["lineage_state"]
        return None