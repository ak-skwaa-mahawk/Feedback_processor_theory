from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .core.knots import Knot, KnotType, Cord
from .core.tag import QuipuTag
from .core.signature import sign_tag
from .algebra import canonical_tag
from .provenance.block import ProvenanceBlock
from .provenance.chain import ProvenanceChain
from .provenance.diff import diff_tags


# ------------------------------------------------------------
# 1. Instruction model
# ------------------------------------------------------------

@dataclass
class Instruction:
    op: str
    args: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------
# 2. VM Context
# ------------------------------------------------------------

@dataclass
class VMContext:
    """
    Holds the working state of the Quipu VM:
      - current_tag: active QuipuTag being mutated
      - registry: named tag store
      - chain: optional provenance chain
      - secret: optional signing secret (for HMAC)
    """
    current_tag: Optional[QuipuTag] = None
    registry: Dict[str, QuipuTag] = field(default_factory=dict)
    chain: Optional[ProvenanceChain] = None
    secret: Optional[bytes] = None

    def ensure_chain(self) -> ProvenanceChain:
        if self.chain is None:
            self.chain = ProvenanceChain()
        return self.chain


# ------------------------------------------------------------
# 3. VM Implementation
# ------------------------------------------------------------

class QuipuVM:
    """
    Simple interpreter for quipu algebra & provenance ops.
    """

    def __init__(self, ctx: Optional[VMContext] = None):
        self.ctx = ctx or VMContext()

    # --------------- core helpers ----------------------------

    def _require_tag(self) -> QuipuTag:
        if self.ctx.current_tag is None:
            raise RuntimeError("No current_tag set in VMContext.")
        return self.ctx.current_tag

    # --------------- instruction execution -------------------

    def execute(self, program: List[Instruction]) -> VMContext:
        """
        Execute a list of Instructions sequentially.
        """
        for instr in program:
            self.step(instr)
        return self.ctx

    def step(self, instr: Instruction) -> None:
        op = instr.op.upper()
        args = instr.args

        if op == "NEW_TAG":
            self.op_new_tag(args)
        elif op == "LOAD":
            self.op_load(args)
        elif op == "SAVE":
            self.op_save(args)
        elif op == "SET_METADATA":
            self.op_set_metadata(args)
        elif op == "ADD_KNOT":
            self.op_add_knot(args)
        elif op == "ADD_CHILD_CORD":
            self.op_add_child_cord(args)
        elif op == "CANONICALIZE":
            self.op_canonicalize()
        elif op == "SIGN":
            self.op_sign(args)
        elif op == "PUSH_BLOCK":
            self.op_push_block(args)
        elif op == "DIFF":
            self.op_diff(args)
        else:
            raise ValueError(f"Unknown opcode: {op}")

    # --------------- ops -------------------------------------

    def op_new_tag(self, args: Dict[str, Any]) -> None:
        """
        NEW_TAG:
          role: str (root role, default "owner")
          color: str (root color, default "gold")
          metadata: dict (optional)
        """
        role = args.get("role", "owner")
        color = args.get("color", "gold")
        metadata = args.get("metadata", {})

        root = Cord(role=role, color=color, knots=[], children=[])
        self.ctx.current_tag = QuipuTag(root_cord=root, metadata=dict(metadata))

    def op_load(self, args: Dict[str, Any]) -> None:
        """
        LOAD:
          name: registry key
        """
        name = args["name"]
        if name not in self.ctx.registry:
            raise KeyError(f"Tag '{name}' not found in registry.")
        self.ctx.current_tag = self.ctx.registry[name]

    def op_save(self, args: Dict[str, Any]) -> None:
        """
        SAVE:
          name: registry key
        """
        name = args["name"]
        tag = self._require_tag()
        self.ctx.registry[name] = tag

    def op_set_metadata(self, args: Dict[str, Any]) -> None:
        """
        SET_METADATA:
          key: str
          value: Any
        """
        tag = self._require_tag()
        key = args["key"]
        value = args["value"]
        tag.metadata[key] = value
        self.ctx.current_tag = tag

    def op_add_knot(self, args: Dict[str, Any]) -> None:
        """
        ADD_KNOT:
          level: int (0 = root, higher = descend into children path index)
          type: str ("single","long","figure8","loop","noose")
          value: int
          path: optional list[int] = indices along children array
        """
        tag = self._require_tag()
        ktype = KnotType(args["type"])
        value = int(args.get("value", 1))
        path = args.get("path", [])

        node = tag.root_cord
        for idx in path:
            if idx < 0 or idx >= len(node.children):
                raise IndexError("Invalid path index while adding knot.")
            node = node.children[idx]

        node.knots.append(Knot(ktype, value))
        self.ctx.current_tag = tag

    def op_add_child_cord(self, args: Dict[str, Any]) -> None:
        """
        ADD_CHILD_CORD:
          role: str
          color: str
          path: optional list[int] to select parent cord (default root)
        """
        tag = self._require_tag()
        role = args["role"]
        color = args.get("color", "gold")
        path = args.get("path", [])

        node = tag.root_cord
        for idx in path:
            if idx < 0 or idx >= len(node.children):
                raise IndexError("Invalid path index while adding child cord.")
            node = node.children[idx]

        node.children.append(Cord(role=role, color=color, knots=[], children=[]))
        self.ctx.current_tag = tag

    def op_canonicalize(self) -> None:
        """
        CANONICALIZE:
          put the current tag into canonical algebraic form.
        """
        tag = self._require_tag()
        self.ctx.current_tag = canonical_tag(tag)

    def op_sign(self, args: Dict[str, Any]) -> None:
        """
        SIGN:
          use either VMContext.secret or provided 'secret' (hex string).
        """
        tag = self._require_tag()
        secret = self.ctx.secret
        if "secret" in args:
            secret = bytes.fromhex(args["secret"])
        sig = sign_tag(tag, secret=secret)
        tag.attach_signature(sig)
        self.ctx.current_tag = tag

    def op_push_block(self, args: Dict[str, Any]) -> None:
        """
        PUSH_BLOCK:
          metadata: dict (optional)
        Creates a new ProvenanceBlock and appends it to the chain.
        """
        tag = self._require_tag()
        chain = self.ctx.ensure_chain()

        idx = len(chain)
        metadata = args.get("metadata", {})
        block = ProvenanceBlock(index=idx, tag=tag, metadata=metadata)
        chain.append(block)
        # nothing else to change; chain is updated in ctx

    def op_diff(self, args: Dict[str, Any]) -> None:
        """
        DIFF:
          other: name of tag in registry to compare with current_tag
        Stores result in ctx.registry["_last_diff"] as a plain dict.
        """
        tag = self._require_tag()
        other_name = args["other"]
        if other_name not in self.ctx.registry:
            raise KeyError(f"Tag '{other_name}' not found for DIFF.")
        other = self.ctx.registry[other_name]
        d = diff_tags(other, tag)
        # store diff as a synthetic registry entry
        self.ctx.registry["_last_diff"] = d