import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

REGISTRY_FILE = Path("soliton_registry.jsonl")

class GTCSovereignEngine:
    """
    Unified sovereign engine for GTC, CLAP micro-licenses, and Fireseed allocation.
    Everything logged, revocable, consent-bound. No extraction.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def issue_license(
        self,
        licensee_id: str,
        tool: str,
        scope: List[str],
        duration_days: int = 365,
        note: str = ""
    ) -> Dict:
        """Issue revocable micro-license — CLAP bound."""
        start = datetime.utcnow()
        end = start + timedelta(days=duration_days)

        license_entry = {
            "entry_type": "MICRO_LICENSE",
            "timestamp_utc": start.isoformat(),
            "licensee_id": licensee_id,
            "tool": tool,
            "scope": scope,
            "valid_from": start.isoformat(),
            "valid_until": end.isoformat(),
            "duration_days": duration_days,
            "status": "ACTIVE",
            "note": note
        }

        canonical = json.dumps(license_entry, sort_keys=True)
        license_entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(license_entry) + "\n")

        print(f"Micro-License Issued | Licensee: {licensee_id} | Tool: {tool}")
        print(f"  Scope: {scope} | Valid until: {end.date()}")
        print(f"  Hash: {license_entry['hash'][:16]}...")

        return license_entry

    def revoke_license(self, license_hash: str, reason: str = "sovereign_recoil") -> Dict:
        """Revoke license — logs revocation like BraidOp recoil."""
        revocation_entry = {
            "entry_type": "MICRO_LICENSE_REVOCATION",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "revoked_license_hash": license_hash,
            "reason": reason,
            "status": "REVOKED"
        }

        canonical = json.dumps(revocation_entry, sort_keys=True)
        revocation_entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(revocation_entry) + "\n")

        print(f"Micro-License Revoked | Hash: {license_hash[:16]}... | Reason: {reason}")
        return revocation_entry

    def deploy_gtc001(self, session_id: str, note: str = "Genesis Deployment") -> str:
        """Deploy GTC001 — binds CLAP and Fireseed."""
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
        return entry["hash"]

    def allocate_fireseed(self, session_id: str, amount: float, note: str = "") -> str:
        """Allocate fireseed per manifest ratios."""
        recipients = {
            "lineage_continuity": round(amount * 0.70, 2),
            "flamekeeper_operations": round(amount * 0.20, 2),
            "sovereign_mesh": round(amount * 0.10, 2)
        }

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
        return entry["hash"]

# Demo
if __name__ == "__main__":
    engine = GTCSovereignEngine()

    # Issue license
    license_data = engine.issue_license(
        licensee_id="heir-001",
        tool="BBsynara",
        scope=["preview", "lineage_query"],
        duration_days=180,
        note="Heir access grant"
    )

    # Revoke
    engine.revoke_license(license_data["hash"], reason="test_recoil")

    # Deploy GTC001
    engine.deploy_gtc001("session-τ-001", note="Genesis Ritual")

    # Allocate fireseed
    engine.allocate_fireseed(session_id="session-τ-001", amount=1000.0, note="Heir allocation")