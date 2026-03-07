from __future__ import annotations
import shlex
import re
import json
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser

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
    braid_hash: Optional[str] = None
    braid_word: Optional[List[Dict]] = None
    tool: Optional[str] = None
    licensee_id: Optional[str] = None
    scope: Optional[List[str]] = None
    duration_days: Optional[int] = None
    license_hash: Optional[str] = None

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
            return self._parse_revoke(tokens, upper_tokens)
        elif action == "CREATE":
            return self._parse_create(tokens, upper_tokens)
        elif action == "ISSUE":
            return self._parse_issue(tokens, upper_tokens)
        else:
            raise SQLTauError(f"Unknown sovereign action: {tokens[0]}")

    # ... (your existing _parse_show, _parse_audit, _parse_snapshot, _parse_revoke unchanged)

    def _parse_create(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 3 or upper_tokens[1] != "BRAID":
            raise SQLTauError("CREATE BRAID ... required")
        # Symbolic or WORD list parsing (your logic)
        for_idx = self._require_keyword(upper_tokens, "FOR", "CREATE BRAID")
        session_id = tokens[for_idx + 1]
        braid_word = []  # parsed from tokens[2:for_idx]
        note = None
        if "NOTE" in upper_tokens:
            note_idx = upper_tokens.index("NOTE")
            note = tokens[note_idx + 1]
        return SQLTauCommand(
            action="CREATE",
            subject="BRAID",
            session_id=session_id,
            braid_word=braid_word,
            note=note
        )

    def _parse_issue(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 6 or upper_tokens[1] != "LICENSE":
            raise SQLTauError("ISSUE LICENSE FOR <tool> TO <licensee> SCOPE [...] DURATION <days>")
        for_idx = self._require_keyword(upper_tokens, "FOR", "ISSUE")
        to_idx = self._require_keyword(upper_tokens, "TO", "ISSUE")
        scope_idx = self._require_keyword(upper_tokens, "SCOPE", "ISSUE")
        duration_idx = self._require_keyword(upper_tokens, "DURATION", "ISSUE")
        tool = tokens[for_idx + 1]
        licensee = tokens[to_idx + 1]
        scope_end = tokens.index("]", scope_idx)
        scope = [t.strip('",') for t in tokens[scope_idx + 1:scope_end]]
        duration_days = int(tokens[duration_idx + 1])
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

    def _dispatch(self, cmd: SQLTauCommand) -> Any:
        if cmd.action == "CREATE" and cmd.subject == "BRAID":
            result = self.braid_layer.log_braid_op(
                session_id=cmd.session_id,
                braid_word=cmd.braid_word,
                note=cmd.note
            )
            Handshake.createReceipt(None, "CREATE-BRAID", {"result": result})
            GlyphParser.parseAndProcess("BRAID-CREATED", None)
            return result
        elif cmd.action == "ISSUE" and cmd.subject == "LICENSE":
            result = self.license_issuer.issue_license(...)  # your issuer logic
            Handshake.createReceipt(None, "ISSUE-LICENSE", {"result": result})
            GlyphParser.parseAndProcess("LICENSE-ISSUED", None)
            return result
        elif cmd.action == "REVOKE" and cmd.subject == "LICENSE":
            result = self.license_issuer.revoke_license(cmd.license_hash)
            Handshake.createReceipt(None, "REVOKE-LICENSE", {"result": result})
            GlyphParser.parseAndProcess("LICENSE-REVOKED", None)
            return result
        # ... keep your existing dispatch for SHOW, AUDIT, SNAPSHOT, REVOKE BRAID

        raise SQLTauError(f"Unhandled action: {cmd.action}")

# Demo
if __name__ == "__main__":
    parser = SQLTauParser()
    queries = [
        'CREATE BRAID B2 B1^-1 B2 FOR session-τ-001 NOTE "post-reclamation"',
        'ISSUE LICENSE FOR "ggwave" TO "researcher.alpha" SCOPE ["read", "broadcast"] DURATION 30 NOTE "cluster-n access"',
        'REVOKE LICENSE abc123... FOR session-τ-001'
    ]
    for q in queries:
        print(f"\n> {q}")
        try:
            result = parser.execute(q)
            print(json.dumps(result, indent=2, default=str))
        except SQLTauError as e:
            print(f"[SQL-τ Error] {e}")