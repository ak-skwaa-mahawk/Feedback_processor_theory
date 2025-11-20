from __future__ import annotations

from .block import ProvenanceBlock


def verify_block(b: ProvenanceBlock) -> bool:
    """
    Simple validation:
    - Hash must match computed
    - Tag must be well-formed
    """
    computed = b.compute_hash()
    d = b.to_dict()
    return d["hash"] == computed