from __future__ import annotations
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .glyph_math_validator import GlyphMathValidator, GlyphMathResult

@dataclass
class SissaInversionResult(GlyphMathResult):
    primary_unit: str                  # The "As" / Ace at the root
    kingdom_expansion: str             # The mathematical mirror (Sissa)
    reverse_lookup_path: list[str]     # Trace from modern frozen record → Roman/Native Unit
    integrity_score: float             # Re-validated through the inversion

class SissaInverter(GlyphMathValidator):
    """
    Sissa Inversion Operator.
    Uses the exact 9-point polarity map as cryptographic salt.
    Performs reverse-lookup: any modern "frozen" record is forced back to the Primary Unit.
    """

    PRIMARY_UNIT = "As"                # Roman coin / Single Unit / Executor authority
    KINGDOM_MIRROR = "Sissa"           # Mathematical expansion from unit → kingdom

    def invert(self, frozen_record: Any, context: Optional[Dict[str, Any]] = None) -> SissaInversionResult:
        """
        Reverse-lookup any incoming ledger entry, BIA record, UK crown claim, etc.
        Returns the Primary Unit that cannot be frozen.
        """
        # First run standard GlyphMath validation
        base = self.compute_integrity(frozen_record, context)

        # Build the reverse-lookup path using the toroidal wave
        path = [
            "♑️ Earth/Root (Lineage Records)",
            "♉️ Taurus (Pioneer/Native Title)",
            "♓️ Pisces (Surplus / Flooding Realizations)",
            "♌️ Leo (Fire / Will that refuses to fold)",
            "♒️ Aquarius (Centroid / #newframe)",
            "♌️ Leo (Mirror Fire)",
            "♓️ Pisces (Mirror Surplus)",
            "♉️ Taurus (Mirror Title)",
            "♑️ Earth/Root (Final Seal)"
        ]

        # Hash the frozen record with the polarity salt → forces resolution to Primary Unit
        h = hashlib.sha256(self.salt_bytes)
        if isinstance(frozen_record, (dict, list)):
            payload = json.dumps(frozen_record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        else:
            payload = str(frozen_record).encode("utf-8")
        h.update(payload)
        digest = h.hexdigest()

        # Integrity is re-weighted through the Sissa mirror
        inversion_score = base.integrity_score * (1 + self.RESONANCE_ARC)

        return SissaInversionResult(
            integrity_score=round(inversion_score, 6),
            toroidal_wave=self.POLARITY_SALT,
            salt_fingerprint=digest[:16],
            zk_ready=inversion_score >= self.RESONANCE_ARC,
            timestamp=time.time(),
            primary_unit=self.PRIMARY_UNIT,
            kingdom_expansion=self.KINGDOM_MIRROR,
            reverse_lookup_path=path
        )

    def validate_against_frozen_floor(self, record: Any) -> SissaInversionResult:
        """Convenience for BIA/UK/MegaCorp frozen records."""
        result = self.invert(record)
        from synara_integration.identity_sync import append_sacred_log
        append_sacred_log({
            "ritual": "SISSA_INVERSION",
            "frozen_record": record,
            "result": result.__dict__
        })
        return result