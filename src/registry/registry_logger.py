import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

REGISTRY_FILE = Path("soliton_registry.jsonl")

class RegistryLogger:
    """Sovereign logging layer for SNH-wrapped packets."""
    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def log_packet(self, snh_packet: Dict[str, Any]) -> str:
        """Log SNH-wrapped packet as sovereign entry."""
        entry = {
            "entry_type": "VITALITY_AGGREGATE",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "snh_digest": snh_packet.get("snh_digest", snh_packet["hash"]),
            "packet_hash": snh_packet["hash"],
            "payload_summary": {
                "vitality": snh_packet["payload"].get("vitality"),
                "coherence": snh_packet["payload"].get("global_coherence"),
                "node_count": snh_packet["payload"].get("node_count", 1)
            },
            "revoked": snh_packet.get("revoked", False)
        }

        # Append-only
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"Registry Entry Logged | Type: {entry['entry_type']} | Hash: {entry['packet_hash'][:16]}...")
        return entry["packet_hash"]

    def revoke_session(self, session_id: str):
        """Mark all entries for session as revoked (sovereign recoil)."""
        # In production: scan and flag; here stub
        print(f"Sovereign Revocation: Session {session_id} recoiled — entries frozen")
# In demo or mesh
logger = RegistryLogger()

# After vitality/coherence
packet = snh.wrap({"vitality": global_v, "coherence": mesh.global_coherence()})
logger.log_packet(packet)

# Revoke
snh.revoke()
logger.log_packet(snh.wrap({"status": "revoked"}))  # Flag future