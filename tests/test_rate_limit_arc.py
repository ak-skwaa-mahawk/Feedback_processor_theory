import time
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_arc_eval_rate_limit():
    # Hit the /arc/eval route more than the short-burst limit (6/10s)
    params = dict(distance_m=10, frequency_hz=3000, medium="air")
    oks, trips = 0, 0
    for i in range(8):
        r = client.get("/arc/eval", params=params)
        if r.status_code == 200:
            oks += 1
        elif r.status_code == 429:
            trips += 1
        else:
            assert False, f"unexpected status: {r.status_code}"
    assert trips >= 1  # should rate-limit within the burst window

def test_rate_limit_headers_present():
    params = dict(distance_m=10, frequency_hz=3000, medium="air")
    r = client.get("/arc/eval", params=params)
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers
    assert "X-RateLimit-Reset" in r.headers