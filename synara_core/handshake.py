import hashlib
import json

class Handshake:
    def __init__(self, node_id="ci-node"):
        self.node_id = node_id

    def create_receipt(self, payload):
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        return {
            "node_id": self.node_id,
            "payload": payload,
            "payload_hash": payload_hash
        }
