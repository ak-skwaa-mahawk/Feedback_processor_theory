import time, httpx

BASE = "http://localhost:8080"

def _hit(n=8, path="/verify", payload=None):
    sizes, durs = [], []
    for _ in range(n):
        t0 = time.perf_counter()
        r = httpx.post(f"{BASE}{path}", json=payload or {"receipt": {"x":"y"}})
        dt = (time.perf_counter() - t0) * 1000
        sizes.append(len(r.content))
        durs.append(dt)
    return sizes, durs

def test_verify_has_padding_and_jitter():
    sizes, durs = _hit()
    # Body should be padded into a narrow band (<= ~2KB variance by default)
    assert (max(sizes) - min(sizes)) <= 2200
    # Latency should include our minimum jitter (~80ms default)
    assert min(durs) >= 70.0