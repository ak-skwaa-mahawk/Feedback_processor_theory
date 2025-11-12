import time, statistics, httpx

BASE = "http://localhost:8080"

def _hit(n=10, path="/verify", payload=None):
    sizes, durs = [], []
    for _ in range(n):
        t0 = time.perf_counter()
        r = httpx.post(f"{BASE}{path}", json=payload or {"receipt": {"x":"y"}})
        dt = (time.perf_counter() - t0) * 1000
        sizes.append(len(r.content))
        durs.append(dt)
    return sizes, durs

def test_verify_shape_is_padded():
    sizes, durs = _hit(12)
    # Size should not be trivially correlated to payload; here we just check small spread
    assert (max(sizes) - min(sizes)) <= 2048  # within configured padding window

    # Latencies should be >= PAD_MIN_MS (80ms default)
    assert min(durs) >= 70.0