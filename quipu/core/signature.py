from __future__ import annotations

import hmac
import hashlib
from typing import Optional

from .tag import QuipuTag
from .encode import canonical_payload


def digest_tag(tag: QuipuTag) -> str:
    payload = canonical_payload(tag)
    return hashlib.sha256(payload).hexdigest()


def sign_tag(tag: QuipuTag, secret: Optional[bytes] = None) -> str:
    payload = canonical_payload(tag)
    if secret is None:
        return hashlib.sha256(payload).hexdigest()
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def verify_tag(tag: QuipuTag, expected_signature: str, secret: Optional[bytes] = None) -> bool:
    actual = sign_tag(tag, secret=secret)
    return hmac.compare_digest(actual, expected_signature)