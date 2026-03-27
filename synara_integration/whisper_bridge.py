from __future__ import annotations
import time
from typing import Dict, Any, Optional, Tuple

try:
    from synara_core.modules.handshake.whisper_handshake_v13 import (
        server_verify,
        VERSION as HS_VERSION,
        DRIFT_MS,
    )
except Exception:
    HS_VERSION = "1.x"
    DRIFT_MS = 180000

    def server_verify(
        receipt: Dict[str, Any],
        expected_challenge: Optional[str] = None,
        max_drift_ms: int = DRIFT_MS,
        challenge_max_age_ms: int = DRIFT_MS,
    ) -> Tuple[bool, str]:
        return False, "ERR_NO_HANDSHAKE_MODULE"

class HandshakeGate:
    """Verifies receipts before allowing FPT analysis."""

    def __init__(self):
        self.version = HS_VERSION

    def verify(
        self, receipt: Dict[str, Any], expected_challenge: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        ok, reason = server_verify(receipt, expected_challenge=expected_challenge)
        context = {}
        if ok:
            context = {
                "kid": str(receipt.get("key_id", "")),
                "aud": str(receipt.get("aud", "-")),
                "scope": str(receipt.get("scope", "-")),
                "entity": str(receipt.get("entity", "")),
                "node": str(receipt.get("node", "")),
                "hs_version": self.version,
            }
        return ok, reason, context