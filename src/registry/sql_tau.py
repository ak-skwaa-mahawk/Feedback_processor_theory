from __future__ import annotations
import shlex
import re
import json
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

# In _parse method, add:
elif action == "SHOW" and "HASH" in ' '.join(upper_tokens):
    return self._parse_show_hash(tokens, upper_tokens)

# New parser method
def _parse_show_hash(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
    resource_type = tokens[2]  # e.g. LICENSE, BRAID, FIRESEED
    resource_id = tokens[4] if len(tokens) > 4 else None
    return SQLTauCommand(
        action="SHOW",
        subject="HASH",
        tool=resource_type,
        licensee_id=resource_id  # reuse field for resource ID
    )

# In _dispatch
elif cmd.action == "SHOW" and cmd.subject == "HASH":
    return self.gtc_engine.get_resource_hash(cmd.tool, cmd.licensee_id)

from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer
from .gtc_sovereign_engine import GTCSovereignEngine   # Unified engine

class SQLTauError(Exception):
    """Sovereign query language error — clear ritual message."""
    pass

@dataclass
class SQLTauCommand:
    action: str
    subject: str
    session_id: Optional[str] = None
    at_time: Optional[str] = None
    note: Optional[str] = None
    braid_word: Optional[List[Dict]] = None
    tool: Optional[str] = None
    licensee_id: Optional[str] = None
    scope: Optional[List[str]] = None
    duration_days: Optional[int] = None
    license_hash: Optional[str] = None
    reason: Optional[str] = None

class SQLTauParser:
    def __init__(
        self,
        engine: Optional[SovereignQueryEngine] = None,
        snapshots: Optional[LineageSnapshots] = None,
        braid_layer: Optional[BraidOpLayer] = None
    ):
        self.engine = engine or SovereignQueryEngine()
        self.snapshots = snapshots or LineageSnapshots()
        self.braid_layer = braid_layer or BraidOpLayer()
        self.gtc_engine = GTCSovereignEngine()

    def execute(self, query: str) -> Any:
        cmd = self._parse(query)
        return self._dispatch(cmd)

    def _parse(self, query: str) -> SQLTauCommand:
        if not query or not query.strip():
            raise SQLTauError("Empty SQL-τ query — speak your intent")

        tokens = shlex.split(query.strip())
        upper_tokens = [t.upper() for t in tokens]
        action = upper_tokens[0]

        if action == "SHOW":
            return self._parse_show(tokens, upper_tokens)
        elif action == "AUDIT":
            return self._parse_audit(tokens, upper_tokens)
        elif action == "SNAPSHOT":
            return self._parse_snapshot(tokens, upper_tokens)
        elif action == "REVOKE":
            if len(upper_tokens) > 1 and upper_tokens[1] == "BRAID":
                return self._parse_revoke_braid(tokens, upper_tokens)
            elif len(upper_tokens) > 1 and upper_tokens[1] == "LICENSE":
                return self._parse_revoke_license(tokens, upper_tokens)
        elif action == "CREATE":
            return self._parse_create_braid(tokens, upper_tokens)
        elif action == "ISSUE":
            return self._parse_issue_license(tokens, upper_tokens)
        elif action == "VERIFY":
            return self._parse_verify_license(tokens, upper_tokens)

        raise SQLTauError(f"Unknown sovereign action: {tokens[0]}")

    # ====================== VERIFY LICENSE ======================
    def _parse_verify_license(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 3 or upper_tokens[1] != "LICENSE":
            raise SQLTauError("VERIFY LICENSE <hash>")

        license_hash = tokens[2]
        return SQLTauCommand(
            action="VERIFY",
            subject="LICENSE",
            license_hash=license_hash
        )

    # ====================== DISPATCH ======================
    def _dispatch(self, cmd: SQLTauCommand) -> Any:
        if cmd.action == "ISSUE" and cmd.subject == "LICENSE":
            return self.gtc_engine.issue_license(
                licensee_id=cmd.licensee_id,
                tool=cmd.tool,
                scope=cmd.scope,
                duration_days=cmd.duration_days,
                note=cmd.note
            )
        elif cmd.action == "REVOKE" and cmd.subject == "LICENSE":
            return self.gtc_engine.revoke_license(cmd.license_hash, reason=cmd.reason or "sovereign_recoil")
        elif cmd.action == "VERIFY" and cmd.subject == "LICENSE":
            return self.gtc_engine.verify_license_by_hash(cmd.license_hash)
        # ... keep all your existing dispatch for SHOW, AUDIT, SNAPSHOT, CREATE BRAID, REVOKE BRAID
        raise SQLTauError(f"Unhandled action: {cmd.action}")