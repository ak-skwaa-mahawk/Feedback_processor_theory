import os
import json
import tempfile
import pytest
from fpt.utils.handshake import handshake_message

def test_handshake_message_default():
    payload = handshake_message("node_ping")
    assert payload["status"] == "success"
    assert payload["message"] == "node_ping"
    assert os.path.exists("logs/handshake_ci.json")

def test_handshake_message_custom_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "custom_handshake.json")
        payload = handshake_message("auth_ack", log_file=target)
        assert payload["status"] == "success"
        assert payload["message"] == "auth_ack"
        assert os.path.exists(target)
        with open(target, "r") as f:
            data = json.load(f)
        assert data == payload
