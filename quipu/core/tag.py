from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .knots import Cord


@dataclass
class QuipuTag:
    version: str = "1.0"
    root_cord: Cord = field(default_factory=lambda: Cord(role="owner"))
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None  # hex digest or external signature

    def without_signature(self) -> "QuipuTag":
        return QuipuTag(
            version=self.version,
            root_cord=self.root_cord,
            metadata=self.metadata.copy(),
            signature=None,
        )

    def to_dict(self, include_signature: bool = True) -> dict:
        d = {
            "version": self.version,
            "root_cord": self.root_cord.to_dict(),
            "metadata": self.metadata,
        }
        if include_signature and self.signature is not None:
            d["signature"] = self.signature
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "QuipuTag":
        return cls(
            version=data.get("version", "1.0"),
            root_cord=Cord.from_dict(data["root_cord"]),
            metadata=data.get("metadata", {}),
            signature=data.get("signature"),
        )

    def attach_signature(self, signature: str) -> None:
        self.signature = signature