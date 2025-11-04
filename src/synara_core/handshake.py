# minimal handshake/receipt
import json
import hashlib
import time
from pathlib import Path

RECEIPT_DIR = Path("/var/lib/synara/receipts")
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Handshake:
    def __init__(self, node_id: str):
        self.node_id = node_id

    def create_receipt(self, payload: dict) -> dict:
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        digest = sha256_hex(payload_bytes)
        receipt = {
            "node_id": self.node_id,
            "ts": int(time.time()),
            "payload_hash": digest,
            "payload": payload,
        }
        filename = RECEIPT_DIR / f"{self.node_id}-{receipt['ts']}-{digest[:8]}.json"
        filename.write_text(json.dumps(receipt, indent=2))
        return receipt

    def verify_receipt(self, receipt: dict) -> bool:
        payload = json.dumps(receipt["payload"], sort_keys=True).encode()
        return sha256_hex(payload) == receipt["payload_hash"]