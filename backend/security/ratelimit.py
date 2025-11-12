import time, threading
from typing import Dict
from backend.config import RL_BUCKET_CAP, RL_REFILL_PER_SEC, REDIS_URL

_USE_REDIS = False
_bucket: Dict[str, Dict[str, float]] = {}
_lock = threading.Lock()

try:
    import redis
    _r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    _r.ping()
    _USE_REDIS = True
except Exception:
    _USE_REDIS = False

def _key(ip: str, route: str) -> str:
    return f"rl:{route}:{ip}"

def allow(ip: str, route: str) -> bool:
    now = time.time()
    if _USE_REDIS:
        k = _key(ip, route)
        pipe = _r.pipeline()
        pipe.hgetall(k)
        curr = pipe.execute()[0] or {}
        tokens = float(curr.get("t", RL_BUCKET_CAP))
        last = float(curr.get("ts", now))
        # refill
        tokens = min(RL_BUCKET_CAP, tokens + (now - last) * RL_REFILL_PER_SEC)
        if tokens < 1.0:
            _r.hset(k, mapping={"t": tokens, "ts": now})
            _r.expire(k, 3600)
            return False
        tokens -= 1.0
        _r.hset(k, mapping={"t": tokens, "ts": now})
        _r.expire(k, 3600)
        return True

    # in-memory
    with _lock:
        rec = _bucket.get((ip, route), {"t": RL_BUCKET_CAP, "ts": now})
        tokens = rec["t"]
        last = rec["ts"]
        tokens = min(RL_BUCKET_CAP, tokens + (now - last) * RL_REFILL_PER_SEC)
        if tokens < 1.0:
            _bucket[(ip, route)] = {"t": tokens, "ts": now}
            return False
        tokens -= 1.0
        _bucket[(ip, route)] = {"t": tokens, "ts": now}
        return True