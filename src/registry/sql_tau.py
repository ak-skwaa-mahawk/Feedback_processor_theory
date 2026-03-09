from __future__ import annotations
import shlex
import re
import json
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer
from .gtc_sovereign_engine import GTCSovereignEngine   # Unified GTC/CLAP/Fireseed engine

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

        raise SQLTauError(f"Unknown sovereign action: {tokens[0]}")

    # ====================== ISSUE LICENSE ======================
    def _parse_issue_license(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 6 or upper_tokens[1] != "LICENSE":
            raise SQLTauError("ISSUE LICENSE FOR <tool> TO <licensee> SCOPE [...] DURATION <days>")

        for_idx = self._require_keyword(upper_tokens, "FOR", "ISSUE LICENSE")
        to_idx = self._require_keyword(upper_tokens, "TO", "ISSUE LICENSE")
        scope_idx = self._require_keyword(upper_tokens, "SCOPE", "ISSUE LICENSE")
        duration_idx = self._require_keyword(upper_tokens, "DURATION", "ISSUE LICENSE")

        tool = tokens[for_idx + 1]
        licensee = tokens[to_idx + 1]

        # Parse scope list
        scope_start = scope_idx + 1
        scope_end = tokens.index("]", scope_start)
        scope = [t.strip('",') for t in tokens[scope_start:scope_end]]

        try:
            duration_days = int(tokens[duration_idx + 1])
        except:
            raise SQLTauError("DURATION requires integer days")

        note = None
        if "NOTE" in upper_tokens:
            note_idx = upper_tokens.index("NOTE")
            note = tokens[note_idx + 1]

        return SQLTauCommand(
            action="ISSUE",
            subject="LICENSE",
            tool=tool,
            licensee_id=licensee,
            scope=scope,
            duration_days=duration_days,
            note=note
        )

    # ====================== REVOKE LICENSE ======================
    def _parse_revoke_license(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 5 or upper_tokens[1] != "LICENSE":
            raise SQLTauError("REVOKE LICENSE <hash> FOR <session-id>")

        license_hash = tokens[2]
        for_idx = self._require_keyword(upper_tokens, "FOR", "REVOKE LICENSE")
        session_id = tokens[for_idx + 1]

        reason = "sovereign_recoil"
        if "REASON" in upper_tokens:
            reason_idx = upper_tokens.index("REASON")
            reason = tokens[reason_idx + 1]

        return SQLTauCommand(
            action="REVOKE",
            subject="LICENSE",
            session_id=session_id,
            license_hash=license_hash,
            reason=reason
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
        # ... keep all your existing dispatch for SHOW, AUDIT, SNAPSHOT, CREATE BRAID, REVOKE BRAID
        raise SQLTauError(f"Unhandled action: {cmd.action}")