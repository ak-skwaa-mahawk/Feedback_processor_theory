import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

REGISTRY_FILE = Path("soliton_registry.jsonl")

class MicroLicenseIssuer:
    """
    Sovereign micro-license issuance — CLAP-bound grants.
    Issues time/scope-limited access to sovereign tools.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path

    def issue_license(
        self,
        licensee_id: str,
        tool: str,  # e.g., "Synara", "BBsynara", "Flamechain"
        scope: List[str],  # e.g., ["preview", "lineage_query"]
        duration_days: int = 365,
        note: str = ""
    ) -> Dict:
        """Issue sovereign micro-license."""
        start = datetime.utcnow()
        end = start + timedelta(days=duration_days)

        license = {
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

        canonical = json.dumps(license, sort_keys=True)
        license["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(license) + "\n")

        print(f"Micro-License Issued | Licensee: {licensee_id} | Tool: {tool}")
        print(f"  Scope: {scope}")
        print(f"  Valid: {start.date()} → {end.date()}")
        print(f"  Hash: {license['hash'][:16]}...")

        return license

    def revoke_license(self, license_hash: str, reason: str = "sovereign_recoil"):
        """Revoke micro-license."""
        entry = {
            "entry_type": "MICRO_LICENSE_REVOCATION",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "revoked_license_hash": license_hash,
            "reason": reason,
            "status": "REVOKED"
        }

        canonical = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"Micro-License Revoked | Hash: {license_hash[:16]}... | Reason: {reason}")

# Demo
if __name__ == "__main__":
    issuer = MicroLicenseIssuer()

    # Issue license
    license = issuer.issue_license(
        licensee_id="heir-001",
        tool="BBsynara",
        scope=["preview", "lineage_query"],
        duration_days=180,
        note="Heir access grant"
    )

    # Revoke (demo)
    issuer.revoke_license(license["hash"])