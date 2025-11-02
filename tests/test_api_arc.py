from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True

def test_eval_basic():
    r = client.get("/arc/eval", params=dict(distance_m=10, frequency_hz=3000, medium="air"))
    assert r.status_code == 200
    data = r.json()
    for k in ["medium","distance_m","frequency_hz","attenuation","return","arc","passes","rgb","audible_0_1"]:
        assert k in data

def test_sweep_list():
    body = {
        "distance_m": 10.0,
        "frequencies_hz": [200.0, 1000.0, 3000.0],
        "medium": "air",
        "threshold": 0.1
    }
    r = client.post("/arc/sweep", json=body)
    assert r.status_code == 200
    out = r.json()
    assert "results" in out
    assert len(out["results"]) == 3