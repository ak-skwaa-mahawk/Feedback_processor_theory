import json
import os

def handshake_message(msg, log_file="logs/handshake_ci.json"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    payload = {"status": "success", "message": msg}
    with open(log_file, "w") as f:
        json.dump(payload, f)
    return payload
