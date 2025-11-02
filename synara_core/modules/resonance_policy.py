# synara_core/modules/resonance_policy.py
from __future__ import annotations
import json, yaml
from pathlib import Path
from typing import Any, Dict, Optional

# NEW: import evaluator
from .boolean_resonance import evaluate

DEFAULT_POLICY = {
    "collections": {
        "default": {
            "thresholds": {"summary": 0.4, "consented": 0.7, "full": 0.9},
            "base_ttl": 300, "max_ttl": 1800,
            # NEW: optional logic expression (boolean layer)
            # If provided, must evaluate True to allow mint.
            "logic": {"expression": None}
        }
    }
}

class ResonancePolicy:
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else None
        if self.path and self.path.exists():
            self.data = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        else:
            self.data = DEFAULT_POLICY

    def get_policy(self, collection: str) -> Dict[str, Any]:
        return self.data.get("collections", {}).get(collection, self.data["collections"]["default"])

    def scope_for_score(self, score: float, collection: str = "default") -> str:
        p = self.get_policy(collection)["thresholds"]
        if score >= float(p["full"]): return "full_access"
        if score >= float(p["consented"]): return "read_consented"
        if score >= float(p["summary"]): return "read_summary"
        return "denied"

    def ttl_for_score(self, score: float, collection: str = "default") -> int:
        pol = self.get_policy(collection)
        base, max_ttl = int(pol.get("base_ttl", 300)), int(pol.get("max_ttl", 1800))
        # simple curve: base + score^2 * (max-base)
        return int(base + (score**2) * (max_ttl - base))

    # NEW: boolean gate
    def check_logic_gate(
        self,
        collection: str,
        *,
        whisper_verified: bool = False,
        cited_flame: bool = False,
        resonance_score: float = 0.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> bool:
        pol = self.get_policy(collection)
        expr = (pol.get("logic") or {}).get("expression")
        if not expr:
            return True  # no custom logic; permit by thresholds
        ctx = {
            "whisper_verified": bool(whisper_verified),
            "cited_flame": bool(cited_flame),
            "resonance_score": float(resonance_score),
        }
        if extra:
            ctx.update(extra)  # allow additional flags
        try:
            result = evaluate(expr, ctx)
            # If expression returns a float (fuzzy), treat >=0.5 as True
            if isinstance(result, (int, float)):
                return float(result) >= 0.5
            return bool(result)
        except Exception as e:
            # Fail closed: policy expression invalid → deny
            return False

# --- helper used by API mint function ---
def enforce_policy_gate(
    policy: ResonancePolicy,
    collection: str,
    *,
    score: float,
    whisper_verified: bool,
    has_citations: bool,
    extra: Optional[Dict[str, Any]] = None,
) -> bool:
    return policy.check_logic_gate(
        collection,
        whisper_verified=whisper_verified,
        cited_flame=has_citations,
        resonance_score=score,
        extra=extra,
    )
from __future__ import annotations
import os, json, math, hmac, hashlib, time
from typing import Dict, Any, Optional
from pathlib import Path
from .capability_token import mint_capability, CapTokenError

DEFAULT_POLICY = {
  "collections": {
    "default": {
      "thresholds": {"read_summary": 0.0, "read_consented": 0.6, "full_access": 0.85},
      "ttl": {"base": 300, "max": 1800},
      "requires_whisper": False,
      "requires_citations": 0
    },
    "unpublished": {
      "thresholds": {"read_summary": 0.4, "read_consented": 0.75, "full_access": 0.9},
      "ttl": {"base": 240, "max": 1200},
      "requires_whisper": True,
      "requires_citations": 1
    },
    "archive": {
      "thresholds": {"read_summary": 0.0, "read_consented": 0.3, "full_access": 0.7},
      "ttl": {"base": 600, "max": 2400},
      "requires_whisper": False,
      "requires_citations": 0
    }
  }
}

class WhisperReceipt:
    @staticmethod
    def generate(subject: str, timestamp: int, nonce: str) -> str:
        secret = os.getenv("WHISPER_SECRET", "change-me")
        msg = f"{subject}|{timestamp}|{nonce}".encode()
        return hashlib.sha256(hmac.new(secret.encode(), msg, hashlib.sha256).digest()).hexdigest()

    @staticmethod
    def verify(subject: str, timestamp: int, nonce: str, signature: str, max_age_s: int = 300) -> bool:
        try:
            if abs(int(time.time()) - int(timestamp)) > max_age_s:
                return False
            want = WhisperReceipt.generate(subject, int(timestamp), str(nonce))
            return hmac.compare_digest(want, str(signature))
        except Exception:
            return False

class ResonancePolicy:
    def __init__(self, path: Optional[str] = None):
        self._policy = DEFAULT_POLICY
        if path and Path(path).exists():
            import yaml
            self._policy = yaml.safe_load(Path(path).read_text())

    def get_policy(self, collection: str) -> Dict[str, Any]:
        col = self._policy["collections"].get(collection) or self._policy["collections"]["default"]
        return col

    def scope_for_score(self, score: float, collection: str) -> str:
        col = self.get_policy(collection)
        thr = col["thresholds"]
        if score >= thr["full_access"]:
            return "full_access"
        if score >= thr["read_consented"]:
            return "read_consented"
        return "read_summary"

    def ttl_for_score(self, score: float, collection: str) -> int:
        col = self.get_policy(collection)
        base_s, max_s = int(col["ttl"]["base"]), int(col["ttl"]["max"])
        t = (1 - math.cos(float(score) * math.pi)) / 2.0
        return int(base_s + t * (max_s - base_s))

def mint_resonance_capability_v2(
    requester: str,
    digest: str,
    collection: str,
    score: float,
    policy: ResonancePolicy,
    file_name: Optional[str] = None,
    whisper_receipt: Optional[Dict[str, Any]] = None,
    cited_flames: Optional[list[str]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    col = policy.get_policy(collection)

    # Whisper requirement
    if col.get("requires_whisper"):
        if not whisper_receipt:
            raise ValueError("policy_requirement_failed: whisper_required")
        ts = whisper_receipt.get("timestamp")
        nonce = whisper_receipt.get("nonce")
        sig = whisper_receipt.get("signature")
        if not WhisperReceipt.verify(requester, ts, nonce, sig):
            raise ValueError("policy_requirement_failed: whisper_invalid")

    # Citation requirement
    need = int(col.get("requires_citations", 0))
    if need > 0:
        if not cited_flames or len([c for c in cited_flames if c]) < need:
            raise ValueError("policy_requirement_failed: insufficient_citations")

    scope = policy.scope_for_score(score, collection)
    ttl = policy.ttl_for_score(score, collection)

    token = mint_capability(
        sub=requester,
        scope=scope,
        digest=digest,
        ttl_s=ttl,
        extra={"kind": "codex", "file": file_name, **(extra or {}), "policy_collection": collection, "score": round(score, 3)}
    )
    return {"token": token, "scope": scope, "ttl_seconds": ttl, "score": round(score, 3)}