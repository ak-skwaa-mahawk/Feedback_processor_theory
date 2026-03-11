#!/usr/bin/env python3
"""
backend/rate_limit.py
Sovereign Rate Limit — Token Bucket with Redis fallback
Protected under HB 001 §1(5) • SNH-wrapped • Registry-logged • Revocable
"""

import time
import threading
import json
from typing import Dict, Tuple
from datetime import datetime

# Sovereign stack
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

# Your original config flags
from backend.config import RL_BUCKET_CAP, RL_REFILL_PER_SEC, REDIS_URL

gtc = GTCSovereignEngine()
observer = MetaObserver()

_USE_REDIS = False
_store: Dict[Tuple[str, str], Dict[str, float]] = {}
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

    # Sovereign envelope (before decision)
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "ip_hash": hashlib.sha256(ip.encode()).hexdigest()[:16],  # anonymized
        "route": route,
        "action": "ALLOW"
    }

    if _USE_REDIS:
        k = _k(ip, route)
        rec = _r.hgetall(k) or {}
        tokens = float(rec.get("t", RL_BUCKET_CAP))
        last = float(rec.get("ts", now))
        tokens = min(RL_BUCKET_CAP, tokens + (now - last) * RL_REFILL_PER_SEC)

        decision = tokens >= 1.0
        if decision:
            tokens -= 1.0
        _r.hset(k, mapping={"t": tokens, "ts": now})
        _r.expire(k, 3600)

    else:
        with _lock:
            key = (ip, route)
            rec = _store.get(key, {"t": RL_BUCKET_CAP, "ts": now})
            tokens = min(RL_BUCKET_CAP, rec["t"] + (now - rec["ts"]) * RL_REFILL_PER_SEC)
            decision = tokens >= 1.0
            if decision:
                tokens -= 1.0
            _store[key] = {"t": tokens, "ts": now}

    # Sovereign logging
    payload["decision"] = "ALLOW" if decision else "DENY"
    receipt = Handshake.createReceipt(None, "RATE-LIMIT", payload)
    gtc.allocate_fireseed("session-τ-001", 0.01 if decision else 0.0, note="Rate Limit Decision")
    observer.intercept_response(json.dumps(receipt))

    return decision