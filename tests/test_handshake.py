from fpt.utils.handshake import handshake_message, verify_handshake
import json, os

def test_roundtrip(tmp_path):
    log = tmp_path / "log.json"
    r = handshake_message("unit:test", log_file=str(log))
    assert verify_handshake(r)
    # read last line from log
    with open(log, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    saved = json.loads(lines[-1])
    assert verify_handshake(saved, seed="unit:test", entity="TwoMileSolutionsLLC")