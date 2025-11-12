"""
Whisper Hardening Helpers

NOTE: This code hardens your *Synara Whisper Handshake*.
It is not related to OpenAI's "Whisper" speech model.
"""

import hmac, hashlib, unicodedata
from typing import Dict

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def canonical_fields(d: Dict) -> Dict:
    # NFC all text-ish fields shallowly
    out = {}
    for k, v in d.items():
        if isinstance(v, str):
            out[k] = nfc(v)
        else:
            out[k] = v
    return out

def sign_hmac_ct(key: bytes, msg: str) -> str:
    # constant-time HMAC-SHA256 hex
    mac = hmac.new(key, msg.encode("utf-8"), hashlib.sha256).hexdigest()
    return mac

def compare_ct(a: str, b: str) -> bool:
    # constant-time compare
    try:
        return hmac.compare_digest(a, b)
    except Exception:
        # equalize timing a bit in weird cases
        return False
"""
Hardening helpers for Synara Whisper Handshake (not OpenAI Whisper).
"""
import hmac, hashlib, unicodedata
from typing import Dict

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def canonical_fields(d: Dict) -> Dict:
    out = {}
    for k, v in d.items():
        out[k] = nfc(v) if isinstance(v, str) else v
    return out

def sign_hmac_ct(key: bytes, msg: str) -> str:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).hexdigest()

def compare_ct(a: str, b: str) -> bool:
    try:
        return hmac.compare_digest(a, b)
    except Exception:
        return False