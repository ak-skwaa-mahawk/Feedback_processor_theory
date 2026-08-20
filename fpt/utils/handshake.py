"""
fpt.utils.handshake
Canonical proof-of-presence and handshake logging.
"""
from __future__ import annotations
import json
import os
from typing import Any, Dict


def handshake_message(msg: str, log_file: str = "logs/handshake_ci.json") -> Dict[str, Any]:
    """Log structured handshake JSON payload."""
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    payload = {"status": "success", "message": msg}
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return payload


def generate_handshake_message(target_file: str = "nullrose_handshake.txt") -> str:
    """Generate handshake verification text payload."""
    message = "RSN Proof of Presence: Verified canonical handshake sequence."
    if os.path.dirname(target_file):
        os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(message + "\n")
    return message
