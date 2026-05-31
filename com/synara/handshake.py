"""
com/synara/handshake.py
Sovereign verification and cryptographic ledger logging engine.
Secures local node transactions with immutable payload hashing.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional

def determine_secure_receipt_directory() -> Path:
    """
    Dynamically falls back to safe fallback directories if system-level 
    var/lib write permissions are not available to the runtime user.
    """
    primary_target = Path("/var/lib/synara/receipts")
    try:
        # Attempt to dry-run establish or probe the targeted root path
        primary_target.mkdir(parents=True, exist_ok=True)
        # Verify active write authority by dropping a brief dotfile marker
        test_file = primary_target / ".write_probe"
        test_file.touch()
        test_file.unlink()
        return primary_target
    except (PermissionError, IOError):
        # Graceful security degradation path: pull user space or OS temp boundaries
        user_home_fallback = Path.home() / ".synara" / "receipts"
        user_home_fallback.mkdir(parents=True, exist_ok=True)
        return user_home_fallback

# Establish state validation directory target
RECEIPT_DIR = determine_secure_receipt_directory()


def sha256_hex(data: bytes) -> str:
    """
    Computes standard SHA-256 string hashes over immutable bitstreams.
    """
    return hashlib.sha256(data).hexdigest()


class Handshake:
    @staticmethod
    def createReceipt(context_token: Optional[str], handshake_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Static validation wrapper satisfying external liaison and call-center 
        no-api pipelines while maintaining local file storage structures.
        """
        # Ensure fallback safety tokens are derived if none are available
        node_id = context_token if context_token else "SYNARA-LIAISON-NODE"
        
        # Consolidate configuration maps into an absolute single-layer footprint
        payload = {
            "handshake_type": handshake_type,
            "data": metadata
        }
        
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = sha256_hex(payload_bytes)
        ts_marker = int(time.time())
        
        receipt = {
            "node_id": node_id,
            "ts": ts_marker,
            "payload_hash": digest,
            "payload": payload,
        }
        
        # Write clean structural ledger files to disk
        filename = RECEIPT_DIR / f"{node_id}-{ts_marker}-{digest[:8]}.json"
        filename.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
        return receipt

    def __init__(self, node_id: str):
        """
        Instance-based instantiator for discrete local multi-agent management.
        """
        self.node_id = node_id

    def create_receipt(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard instance wrapper tracking state payloads over local system loops.
        """
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = sha256_hex(payload_bytes)
        ts_marker = int(time.time())
        
        receipt = {
            "node_id": self.node_id,
            "ts": ts_marker,
            "payload_hash": digest,
            "payload": payload,
        }
        
        filename = RECEIPT_DIR / f"{self.node_id}-{ts_marker}-{digest[:8]}.json"
        filename.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
        return receipt

    def verify_receipt(self, receipt: Dict[str, Any]) -> bool:
        """
        Audits incoming receipt arrays by evaluating raw contents against the target hash.
        """
        try:
            if "payload" not in receipt or "payload_hash" not in receipt:
                return False
            payload_bytes = json.dumps(receipt["payload"], sort_keys=True).encode("utf-8")
            return sha256_hex(payload_bytes) == receipt["payload_hash"]
        except (KeyError, TypeError, ValueError):
            return False

if __name__ == "__main__":
    # Self-contained integration verification block
    print(f"🔒 Cryptographic Ledger Active Target: {RECEIPT_DIR}")
    
    # Verify Instance Engine Operations
    tester = Handshake(node_id="LOCAL-NODE-001")
    sample_payload = {"vector": "Tordial-GS-Manifold-Calculations", "value": 1.04159}
    receipt_block = tester.create_receipt(sample_payload)
    print(f"✅ Instance Receipt Generated: 0x{receipt_block['payload_hash'][:16]}...")
    print(f"⚖️ Cryptographic Integrity Verified: {tester.verify_receipt(receipt_block)}")
