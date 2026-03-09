import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

REGISTRY_FILE = Path("soliton_registry.jsonl")

class GTCSovereignEngine:
    """
    Unified sovereign engine for GTC, CLAP micro-licenses, and Fireseed allocation.
    Every license is signed with Ed25519 and logged immutably.
    """

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.path = registry_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Load or generate Ed25519 key pair (store private key securely offline)
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def sign_license(self, license_dict: Dict) -> str:
        """Sign the license with Ed25519."""
        canonical = json.dumps(license_dict, sort_keys=True).encode()
        signature = self.private_key.sign(canonical)
        return signature.hex()

    def verify_license(self, license_dict: Dict, signature_hex: str) -> bool:
        """Verify signature on a license."""
        try:
            signature = bytes.fromhex(signature_hex)
            canonical = json.dumps(license_dict, sort_keys=True).encode()
            self.public_key.verify(signature, canonical)
            return True
        except:
            return False

    def issue_license(
        self,
        licensee_id: str,
        tool: str,
        scope: List[str],
        duration_days: int = 365,
        note: str = ""
    ) -> Dict:
        """Issue revocable micro-license with cryptographic signature."""
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

        # Sign before hashing
        license_entry["signature"] = self.sign_license(license_entry)

        canonical = json.dumps(license_entry, sort_keys=True)
        license_entry["hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        with self.path.open("a") as f:
            f.write(json.dumps(license_entry) + "\n")

        print(f"Micro-License Issued & Signed | Licensee: {licensee_id} | Tool: {tool}")
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

    # ... (your existing deploy_gtc001 and allocate_fireseed methods remain unchanged)

def verify_license_by_hash(self, license_hash: str) -> Dict:
    """Lookup license by hash and verify its Ed25519 signature."""
    if not self.path.exists():
        return {"status": "NOT_FOUND"}

    with self.path.open() as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("hash") == license_hash and entry.get("entry_type") == "MICRO_LICENSE":
                    sig = entry.get("signature")
                    if not sig:
                        return {"status": "NO_SIGNATURE", "valid": False}
                    valid = self.verify_license(entry, sig)
                    return {
                        "status": "VERIFIED" if valid else "INVALID_SIGNATURE",
                        "valid": valid,
                        "licensee_id": entry.get("licensee_id"),
                        "tool": entry.get("tool"),
                        "valid_until": entry.get("valid_until")
                    }
            except:
                continue
    return {"status": "NOT_FOUND", "valid": False}