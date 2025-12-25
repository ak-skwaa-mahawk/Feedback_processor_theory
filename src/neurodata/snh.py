import time
import hashlib
import json

class SNH:
    """
    Sovereign Neurodata Header (SNH)
    Wraps any vitality/coherence packet with:
    - consent
    - retention
    - revocation
    - timestamp
    - witness id (pseudonymous)
    - content hash
    """

    def __init__(self, witness_id: str, retention_sec: int = 3600):
        self.witness_id = witness_id
        self.retention_sec = retention_sec
        self.revoked = False

    def wrap(self, payload: dict) -> dict:
        """
        Wrap a vitality/coherence packet with sovereign metadata.
        payload: dict of aggregates (no raw EEG)
        """
        ts = time.time()

        body = {
            "timestamp": ts,
            "witness_id": self.witness_id,
            "retention_sec": self.retention_sec,
            "revoked": self.revoked,
            "payload": payload,
        }

        # Hash for integrity
        encoded = json.dumps(body, sort_keys=True).encode()
        body["hash"] = hashlib.sha256(encoded).hexdigest()

        return body

    def revoke(self):
        """Mark header as revoked."""
        self.revoked = True