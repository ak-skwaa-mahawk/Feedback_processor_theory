import json
from fastapi.testclient import TestClient
from api.codex import app  # adjust import if your app is elsewhere

client = TestClient(app)

def test_policy_dry_run_boolean():
    resp = client.post("/policy/dry_run", json={
        "expression": "(whisper_verified and cited_flame) or (resonance_score > 0.85)",
        "context": {"whisper_verified": True, "cited_flame": False, "resonance_score": 0.88}
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "ok"
    assert data["boolean"] is True

def test_policy_dry_run_fuzzy():
    resp = client.post("/policy/dry_run", json={
        "expression": "AND(resonance_score, 0.9)",
        "context": {"resonance_score": 0.86},
        "coerce_fuzzy_to_bool": True
    })
    assert resp.status_code == 200
    data = resp.json()
    # AND(0.86, 0.9) = 0.86 → boolean True when coerced (>=0.5)
    assert abs(float(data["value"]) - 0.86) < 1e-9
    assert data["boolean"] is True

def test_policy_dry_run_disallowed():
    # Disallow dangerous constructs
    resp = client.post("/policy/dry_run", json={
        "expression": "__import__('os').system('echo nope')",
        "context": {}
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "error"