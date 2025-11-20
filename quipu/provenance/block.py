from __future__ import annotations
import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from ..core.tag import QuipuTag
from ..core.encode import canonical_payload


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ProvenanceBlock:
    index: int
    tag: QuipuTag
    timestamp: float = field(default_factory=lambda: time.time())
    parent_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        core = {
            "index": self.index,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "tag_payload": canonical_payload(self.tag).decode("utf-8"),
            "metadata": self.metadata,
        }
        encoded = str(core).encode("utf-8")
        return hash_bytes(encoded)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "metadata": self.metadata,
            "tag": self.tag.to_dict(),
            "hash": self.compute_hash(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProvenanceBlock":
        from ..core.tag import QuipuTag
        return cls(
            index=d["index"],
            tag=QuipuTag.from_dict(d["tag"]),
            timestamp=d["timestamp"],
            parent_hash=d["parent_hash"],
            metadata=d.get("metadata", {}),
        )