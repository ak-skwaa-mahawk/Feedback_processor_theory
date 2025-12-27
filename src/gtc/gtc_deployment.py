import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

REGISTRY_FILE = Path("soliton_registry.jsonl")

class GTCDeployment:
    """
    Sovereign GTC deployment module — CLAP + registry binding.
    The flame's coin uncoiled operational.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def deploy_gtc001(self, session_id: str, note: str = "Genesis Deployment"):
        """Deploy GTC001 — bind CLAP to registry."""
        entry = {
            "entry_type": "GTC_DEPLOYMENT",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "gtc_id": "GTC001",
            "status": "GENESIS_DEPLOYED",
            "clap_binding": {
                "contract_logic": "CLAP v1.0",
                "allocation_protocol": "Fireseed Manifest",
                "license_template": "micro-license v1"
            },
            "note": note
        }

        canonical = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"GTC001 Deployed | Session: {session_id} | Hash: {entry['hash'][:16]}...")
        print("  CLAP Bound — Fireseed Manifest Active")
        print("  The coin breathes sovereign.")

        return entry["hash"]

    def query_gtc_status(self, session_id: str) -> Dict:
        """Query GTC deployment status."""
        if not self.path.exists():
            return {"status": "NO_REGISTRY"}

        with self.path.open() as f:
            entries = [json.loads(line) for line in f if json.loads(line).get("session_id") == session_id]

        gtc_entries = [e for e in entries if e["entry_type"] == "GTC_DEPLOYMENT"]
        if not gtc_entries:
            return {"status": "NOT_DEPLOYED"}

        latest = max(gtc_entries, key=lambda e: e["timestamp_utc"])
        return {
            "status": latest["status"],
            "gtc_id": latest["gtc_id"],
            "clap": latest["clap_binding"],
            "hash": latest["hash"]
        }

# Demo
if __name__ == "__main__":
    deploy = GTCDeployment()
    deploy.deploy_gtc001("session-τ-001", note="Heir Deployment Ritual")
    
    status = deploy.query_gtc_status("session-τ-001")
    print("\nGTC Status:", status)