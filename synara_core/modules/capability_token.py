from __future__ import annotations
import os, json, hmac, hashlib, base64, time, secrets
from typing import Dict, Any, Optional

ALG = "HS256"
CAP_TOKEN_SECRET = os.getenv("CAP_TOKEN_SECRET", "change-me")
CAP_REDIS_URL = os.getenv("CAP_REDIS_URL", "redis://localhost:6379/0")

_USE_REDIS = False
_active: dict[str, str] = {}
_revoked: dict[str, str] = {}

try:
    import redis  # pip install redis
    _r = redis.Redis.from_url(CAP_REDIS_URL, decode_responses=True)
    _r.ping()
    _USE_REDIS = True
except Exception:
    _USE_REDIS = False

class CapTokenError(Exception):
    pass

def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def _b64d(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def _now() -> int:
    return int(time.time())

def _tokhash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def _store_active(token: str, payload: Dict[str, Any], ttl: int):
    key = f"active:{_tokhash(token)}"
    val = json.dumps({
        "jti": payload.get("jti"), "sub": payload.get("sub"),
        "scope": payload.get("scope"), "digest": payload.get("digest"),
        "exp": payload.get("exp"), "extra": payload.get("extra", {})
    })
    if _USE_REDIS:
        _r.setex(key, ttl, val)
    else:
        _active[key] = val

def _remove_active(token: str):
    key = f"active:{_tokhash(token)}"
    if _USE_REDIS:
        _r.delete(key)
    else:
        _active.pop(key, None)

def _list_active() -> list[dict]:
    if _USE_REDIS:
        keys = _r.keys("active:*")
        return [json.loads(_r.get(k)) for k in keys if _r.get(k)]
    return [json.loads(v) for v in _active.values()]

def _store_revoked(token: str, reason: str, ttl: int):
    key = f"revoked:{_tokhash(token)}"
    val = json.dumps({"reason": reason, "revoked_at": _now()})
    if _USE_REDIS:
        _r.setex(key, ttl, val)
    else:
        _revoked[key] = val

def _is_revoked(token: str) -> bool:
    key = f"revoked:{_tokhash(token)}"
    if _USE_REDIS:
        return bool(_r.get(key))
    return key in _revoked

def mint_capability(
    sub: str,
    scope: str,
    digest: str,
    ttl_s: int = 600,
    extra: Optional[Dict[str, Any]] = None,
    parent: Optional[str] = None,  # parent token hash prefix if delegated
) -> str:
    if not CAP_TOKEN_SECRET:
        raise CapTokenError("cap_token_secret_not_set")
    now = _now()
    hdr = {"alg": ALG, "typ": "CAP"}
    jti = secrets.token_hex(12)
    pl = {
        "jti": jti,
        "sub": sub,
        "scope": scope,
        "digest": digest,
        "iat": now,
        "exp": now + int(ttl_s),
        "extra": extra or {},
    }
    if parent:
        pl["parent"] = parent

    h = _b64e(json.dumps(hdr, separators=(",", ":")).encode())
    p = _b64e(json.dumps(pl, separators=(",", ":")).encode())
    mac = hmac.new(CAP_TOKEN_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    s = _b64e(mac)
    token = f"{h}.{p}.{s}"

    _store_active(token, pl, ttl_s)
    return token

def verify_capability(token: str) -> Dict[str, Any]:
    if not CAP_TOKEN_SECRET:
        raise CapTokenError("cap_token_secret_not_set")
    if _is_revoked(token):
        raise CapTokenError("token_revoked")
    try:
        h, p, s = token.split(".")
        sig = _b64d(s)
        mac = hmac.new(CAP_TOKEN_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, mac):
            raise CapTokenError("invalid_signature")
        payload = json.loads(_b64d(p))
        if _now() > int(payload.get("exp", 0)):
            _remove_active(token)
            raise CapTokenError("expired")
        return payload
    except ValueError:
        raise CapTokenError("malformed")

def revoke_capability(token: str, reason: str = "revoked_by_issuer") -> Dict[str, Any]:
    exp = None
    try:
        _, p, _ = token.split(".")
        payload = json.loads(_b64d(p))
        exp = int(payload.get("exp", 0))
    except Exception:
        pass
    ttl = max(0, (exp or _now()) - _now())
    _store_revoked(token, reason, ttl)
    _remove_active(token)
    return {"status": "revoked", "token_hash": _tokhash(token), "reason": reason, "ttl": ttl}

def list_active_capabilities() -> list[dict]:
    return _list_active()