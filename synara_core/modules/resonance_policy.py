import json, os, hmac, hashlib, base64, time
from pathlib import Path
from typing import Optional

import yaml

class ResonancePolicy:
    def __init__(self, policy_path: Optional[str] = None):
        self.cfg = self._load(policy_path)

    def _load(self, path):
        default = {
            "collections": {
                "default": {
                    "thresholds": {"read_summary": 0.3, "read_consented": 0.6, "full_access": 0.9},
                    "ttls": {"base": 300, "max": 1800}
                },
                "unpublished": {
                    "require_whisper": True,
                    "require_citations": 1,
                    "thresholds": {"read_summary": 0.6, "read_consented": 0.8, "full_access": 0.95},
                    "ttls": {"base": 300, "max": 900}
                },
                "archive": {
                    "thresholds": {"read_summary": 0.3, "read_consented": 0.5, "full_access": 0.8},
                    "ttls": {"base": 600, "max": 3600}
                }
            }
        }
        if path and Path(path).exists():
            return yaml.safe_load(Path(path).read_text()) or default
        return default

    def get_policy(self, collection: str):
        return self.cfg["collections"].get(collection, self.cfg["collections"]["default"])

    def scope_for_score(self, score: float, collection: str = "default") -> str:
        th = self.get_policy(collection)["thresholds"]
        if score >= th["full_access"]: return "full_access"
        if score >= th["read_consented"]: return "read_consented"
        if score >= th["read_summary"]: return "read_summary"
        return "denied"

    def ttl_for_score(self, score: float, collection: str = "default") -> int:
        ttls = self.get_policy(collection)["ttls"]
        base, maxv = ttls.get("base", 300), ttls.get("max", 1800)
        # simple linear scaling
        s = max(0.0, min(1.0, score))
        return int(min(maxv, base + s * (maxv - base)))

class WhisperReceipt:
    SECRET = os.getenv("WHISPER_SECRET", "change-me-whisper")

    @classmethod
    def generate(cls, requester: str, timestamp: int, nonce: str) -> str:
        msg = f"{requester}|{timestamp}|{nonce}".encode()
        mac = hmac.new(cls.SECRET.encode(), msg, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(mac).decode().rstrip("=")

    @classmethod
    def verify(cls, requester: str, timestamp: int, nonce: str, signature: str, max_age_s=300) -> bool:
        if abs(int(time.time()) - int(timestamp)) > max_age_s:
            return False
        want = cls.generate(requester, int(timestamp), nonce)
        return hmac.compare_digest(want, signature)

def mint_resonance_capability_v2(
    requester: str,
    digest: str,
    collection: str,
    score: float,
    policy: ResonancePolicy,
    file_name: str,
    whisper_receipt: dict | None = None,
    cited_flames: list[str] | None = None,
    extra: dict | None = None,
):
    from synara_core.modules.capability_token import mint_capability, CapTokenError

    pol = policy.get_policy(collection)
    scope = policy.scope_for_score(score, collection)

    if pol.get("require_whisper"):
        if not whisper_receipt:
            raise ValueError("policy_requirement_failed: missing_whisper")
        ok = WhisperReceipt.verify(
            requester=requester,
            timestamp=whisper_receipt.get("timestamp"),
            nonce=whisper_receipt.get("nonce"),
            signature=whisper_receipt.get("signature"),
        )
        if not ok:
            raise ValueError("policy_requirement_failed: invalid_whisper")

    req_cites = int(pol.get("require_citations", 0))
    if req_cites > 0:
        if not cited_flames or len([c for c in cited_flames if c]) < req_cites:
            raise ValueError("policy_requirement_failed: insufficient_citations")

    if scope == "denied":
        raise ValueError("policy_requirement_failed: insufficient_score")

    ttl = policy.ttl_for_score(score, collection)
    token = mint_capability(
        sub=requester,
        scope=scope,
        digest=digest,
        ttl_s=ttl,
        extra={"kind": "codex", "file": file_name, **(extra or {})}
    )
    return {"token": token, "scope": scope, "expires_in": ttl}