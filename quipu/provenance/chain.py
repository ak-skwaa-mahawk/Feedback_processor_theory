from __future__ import annotations
from typing import List, Optional

from .block import ProvenanceBlock
from .verify import verify_block


class ProvenanceChain:
    def __init__(self):
        self.blocks: List[ProvenanceBlock] = []

    # ------------------------------------------------------------
    # Create new block
    # ------------------------------------------------------------
    def append(self, block: ProvenanceBlock):
        """
        Append a block to the chain only if it validates.
        """
        if not self.blocks:
            # Genesis block
            block.parent_hash = None
        else:
            parent = self.blocks[-1]
            block.parent_hash = parent.compute_hash()

            # Validate parent linkage
            if block.parent_hash != parent.compute_hash():
                raise ValueError("Parent hash mismatch; block rejected.")

        # Validate block structure
        if not verify_block(block):
            raise ValueError("Block failed validation.")

        self.blocks.append(block)

    # ------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------
    def latest(self) -> Optional[ProvenanceBlock]:
        return self.blocks[-1] if self.blocks else None

    def __len__(self):
        return len(self.blocks)

    def to_dict(self):
        return [b.to_dict() for b in self.blocks]

    @classmethod
    def from_dict(cls, arr: list) -> "ProvenanceChain":
        c = cls()
        for d in arr:
            b = ProvenanceBlock.from_dict(d)
            c.append(b)
        return c