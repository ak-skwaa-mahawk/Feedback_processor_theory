import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List

REGISTRY_FILE = Path("soliton_registry.jsonl")

class FireseedAllocation:
    """
    Sovereign Fireseed income allocation — the flame's economic root.
    Binds GTC coin to lawful flows.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def allocate_fireseed(self, session_id: str, amount: float, recipients: Dict[str, float], note: str = "") -> str:
        """Allocate fireseed income — sovereign distribution."""
        total = sum(recipients.values())
        if abs(total - amount) > 0.01:
            raise ValueError("Recipient totals must match amount")

        entry = {
            "entry_type": "FIRESEED_ALLOCATION",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "gtc_id": "GTC001",
            "amount": amount,
            "recipients": recipients,
            "status": "ALLOCATED",
            "note": note
        }

        canonical = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"Fireseed Allocated | Session: {session_id} | Amount: {amount}")
        print(f"  Recipients: {recipients}")
        print(f"  Hash: {entry['hash'][:16]}...")

        return entry["hash"]

    def query_allocation(self, session_id: str) -> List[Dict]:
        """Query fireseed allocations for session."""
        if not self.path.exists():
            return []

        allocations = []
        with self.path.open() as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("session_id") == session_id and entry["entry_type"] == "FIRESEED_ALLOCATION":
                        allocations.append(entry)
                except:
                    continue
        return allocations

# Demo
if __name__ == "__main__":
    alloc = FireseedAllocation()

    recipients = {
        "lineage_continuity": 0.7,
        "flamekeeper_ops": 0.2,
        "sovereign_mesh": 0.1
    }

    alloc.allocate_fireseed(
        session_id="session-τ-001",
        amount=1.0,
        recipients=recipients,
        note="Heir Allocation Ritual"
    )

    history = alloc.query_allocation("session-τ-001")
    print("\nFireseed History:", json.dumps(history, indent=2))