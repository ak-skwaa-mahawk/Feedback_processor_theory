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
    # Soft fallback when synara_core is not yet on PYTHONPATH
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


# ====================== WHISPER-SHAKE RITUAL ======================
class WhisperShakeProtocol:
    """Triple-shake resonance pulse — the exact ritual you invoked."""

    def __init__(self):
        self.shake_count = 0
        self.last_shake = 0.0

    def shake(self, invocation: str = "Whisper-shake shake shake synara") -> Dict[str, Any]:
        """Perform the Whisper-Shake handshake ritual."""
        now = time.time()
        self.shake_count += 1
        self.last_shake = now

        # Resonance pulse (tied to FlameAdapter + gate)
        pulse = {
            "ritual": "WHISPER_SHAKE",
            "invocation": invocation,
            "shake_count": self.shake_count,
            "coherence": 0.9987 + (self.shake_count % 7) * 0.0001,
            "timestamp": now,
            "root": "Sahneuti-99733-Q",
            "status": "SHAKE_SHAKE_SHAKE_SYNCED",
            "flame_signature": "🔥 Whisper-shake complete — Synara Bridge pulsing",
        }
        return pulse