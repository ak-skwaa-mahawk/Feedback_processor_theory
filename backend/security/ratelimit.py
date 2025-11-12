import time, threading
from typing import Dict
from backend.config import RL_BUCKET_CAP, RL_REFILL_PER_SEC, REDIS_URL

_USE_REDIS = False
_store: Dict[tuple, Dict[str, float]] = {}
_lock = threading.Lock()

try:
    import redis
    _r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    _r.ping()
    _USE_REDIS = True
except Exception:
    _USE_REDIS = False

def _k(ip: str, route: str) -> str:
    return f"rl:{route}:{ip}"

def allow(ip: str, route: str) -> bool:
    now = time.time()
    if _USE_REDIS:
        k = _k(ip, route)
        rec = _r.hgetall(k) or {}
        tokens = float(rec.get("t", RL_BUCKET_CAP))
        last = float(rec.get("ts", now))
        tokens = min(RL_BUCKET_CAP, tokens + (now - last) * RL_REFILL_PER_SEC)
        if tokens < 1.0:
            _r.hset(k, mapping={"t": tokens, "ts": now}); _r.expire(k, 3600)
            return False
        tokens -= 1.0
        _r.hset(k, mapping={"t": tokens, "ts": now}); _r.expire(k, 3600)
        return True

    with _lock:
        rec = _store.get((ip, route), {"t": RL_BUCKET_CAP, "ts": now})
        tokens = min(RL_BUCKET_CAP, rec["t"] + (now - rec["ts"]) * RL_REFILL_PER_SEC)
        if tokens < 1.0:
            _store[(ip, route)] = {"t": tokens, "ts": now}
            return False
        tokens -= 1.0
        _store[(ip, route)] = {"t": tokens, "ts": now}
        return True