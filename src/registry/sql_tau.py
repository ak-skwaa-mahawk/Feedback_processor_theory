import shlex
import re
from typing import Any, Optional
from dataclasses import dataclass

from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer

class SQLTauError(Exception):
    """Sovereign query language error — clear ritual message."""
    pass

@dataclass
class SQLTauCommand:
    """Parsed SQL-τ command."""
    action: str
    subject: str
    session_id: Optional[str] = None
    at_time: Optional[str] = None
    note: Optional[str] = None
    braid_hash: Optional[str] = None

class SQLTauParser:
    """
    Hardened Sovereign Query Language (SQL-τ) parser + interpreter.
    - Preserves arguments (session IDs, timestamps, hashes)
    - Normalizes only keywords
    - Clear error rituals
    - Extended sovereign commands
    """

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
        """Parse and execute SQL-τ query."""
        cmd = self._parse(query)
        return self._dispatch(cmd)

    def _parse(self, query: str) -> SQLTauCommand:
        if not query or not query.strip():
            raise SQLTauError("Empty SQL-τ query — speak your intent")

        tokens = shlex.split(query.strip())
        if not tokens:
            raise SQLTauError("Empty SQL-τ query — no words spoken")

        # Uppercase only keywords for matching, preserve original args
        upper_tokens = [t.upper() for t in tokens]

        action = upper_tokens[0]
        if action not in {"SHOW", "AUDIT", "SNAPSHOT", "REVOKE"}:
            raise SQLTauError(f"Unknown sovereign action: {tokens[0]} — speak SHOW, AUDIT, SNAPSHOT, or REVOKE")

        if action == "SHOW":
            return self._parse_show(tokens, upper_tokens)
        elif action == "AUDIT":
            return self._parse_audit(tokens, upper_tokens)
        elif action == "SNAPSHOT":
            return self._parse_snapshot(tokens, upper_tokens)
        elif action == "REVOKE":
            return self._parse_revoke(tokens, upper_tokens)

        raise SQLTauError(f"Unhandled action: {tokens[0]}")

    def _require_keyword(self, upper_tokens: List[str], keyword: str, context: str) -> int:
        try:
            return upper_tokens.index(keyword)
        except ValueError:
            raise SQLTauError(f"Expected '{keyword}' in {context}")

    def _parse_for_session(self, tokens: List[str], upper_tokens: List[str], start_idx: int) -> str:
        for_idx = self._require_keyword(upper_tokens, "FOR", "query")
        if for_idx + 1 >= len(tokens):
            raise SQLTauError("Missing session ID after 'FOR'")
        return tokens[for_idx + 1]

    def _parse_show(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        # SHOW [ACTIVE|REVOKED] BRAIDS FOR <session>
        # SHOW [BRAID HISTORY|FUSION TIMELINE|SNAPSHOTS|LAST SNAPSHOT] FOR <session>
        # SHOW LINEAGE AT "time" FOR <session>

        if len(upper_tokens) < 2:
            raise SQLTauError("SHOW requires a subject — speak what you seek")

        subject_parts = upper_tokens[1:]
        subject = " ".join(subject_parts[:2] if len(subject_parts) >= 2 else subject_parts)

        if subject in {"ACTIVE BRAIDS", "REVOKED BRAIDS", "BRAID HISTORY", "FUSION TIMELINE", "SNAPSHOTS", "LAST SNAPSHOT"}:
            session_id = self._parse_for_session(tokens, upper_tokens, 2)
            return SQLTauCommand(action="SHOW", subject=subject.replace(" ", "_"), session_id=session_id)

        if subject_parts[0] == "LINEAGE":
            at_idx = self._require_keyword(upper_tokens, "AT", "SHOW LINEAGE")
            for_idx = self._require_keyword(upper_tokens, "FOR", "SHOW LINEAGE")

            if at_idx + 1 >= len(tokens) or for_idx + 1 >= len(tokens):
                raise SQLTauError("SHOW LINEAGE requires AT <time> and FOR <session>")

            at_time = tokens[at_idx + 1]
            session_id = tokens[for_idx + 1]
            return SQLTauCommand(action="SHOW", subject="LINEAGE_AT_TIME", session_id=session_id, at_time=at_time)

        raise SQLTauError(f"Unrecognized SHOW subject: {' '.join(tokens[1:3])}")

    def _parse_audit(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 3 or upper_tokens[1] != "SESSION":
            raise SQLTauError("AUDIT requires SESSION <session-id>")
        session_id = tokens[2]
        return SQLTauCommand(action="AUDIT", subject="SESSION", session_id=session_id)

    def _parse_snapshot(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 4 or upper_tokens[1] != "LINEAGE" or upper_tokens[2] != "FOR":
            raise SQLTauError("SNAPSHOT LINEAGE FOR <session-id> [NOTE \"text\"]")
        session_id = tokens[3]

        note = None
        if "NOTE" in upper_tokens:
            note_idx = upper_tokens.index("NOTE")
            if note_idx + 1 >= len(tokens):
                raise SQLTauError("NOTE requires quoted text")
            note = tokens[note_idx + 1]

        return SQLTauCommand(action="SNAPSHOT", subject="LINEAGE", session_id=session_id, note=note)

    def _parse_revoke(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 5 or upper_tokens[1] != "BRAID" or upper_tokens[3] != "FOR":
            raise SQLTauError("REVOKE BRAID <hash> FOR <session-id>")
        braid_hash = tokens[2]
        session_id = tokens[4]
        return SQLTauCommand(action="REVOKE", subject="BRAID", session_id=session_id, braid_hash=braid_hash)

    def _dispatch(self, cmd: SQLTauCommand) -> Any:
        if cmd.action == "SHOW":
            return self._dispatch_show(cmd)
        if cmd.action == "AUDIT":
            return self.engine.query_constitutional_audit(cmd.session_id)
        if cmd.action == "SNAPSHOT":
            return self.snapshots.snapshot_lineage(cmd.session_id, note=cmd.note)
        if cmd.action == "REVOKE":
            return self.braid_layer.revoke(cmd.session_id, cmd.braid_hash)

        raise SQLTauError(f"Unhandled action: {cmd.action}")

    def _dispatch_show(self, cmd: SQLTauCommand) -> Any:
        subject = cmd.subject
        if subject == "ACTIVE_BRAIDS":
            return self.engine.query_active_braids(cmd.session_id)
        if subject == "REVOKED_BRAIDS":
            return self.engine.query_revoked_braids(cmd.session_id)
        if subject == "BRAID_HISTORY":
            return self.engine.query_braid_history(cmd.session_id)
        if subject == "FUSION_TIMELINE":
            return self.engine.query_fusion_timeline(cmd.session_id)
        if subject == "SNAPSHOTS":
            return self.snapshots.show_snapshots(cmd.session_id)
        if subject == "LAST_SNAPSHOT":
            snaps = self.snapshots.show_snapshots(cmd.session_id)
            return snaps[-1] if snaps else None
        if subject == "LINEAGE_AT_TIME":
            return self.engine.query_lineage_at_time(cmd.session_id, cmd.at_time)

        raise SQLTauError(f"Unknown SHOW subject: {subject}")

# Demo
if __name__ == "__main__":
    parser = SQLTauParser()

    queries = [
        'SHOW ACTIVE BRAIDS FOR session-τ-001',
        'SHOW REVOKED BRAIDS FOR session-τ-001',
        'SHOW LINEAGE AT "2025-12-25T21:30:00" FOR session-τ-001',
        'SHOW BRAID HISTORY FOR session-τ-001',
        'SHOW FUSION TIMELINE FOR session-τ-001',
        'SHOW SNAPSHOTS FOR session-τ-001',
        'SHOW LAST SNAPSHOT FOR session-τ-001',
        'AUDIT SESSION session-τ-001',
        'SNAPSHOT LINEAGE FOR session-τ-001 NOTE "post-reflection"',
        'REVOKE BRAID abc123... FOR session-τ-001',
    ]

    for q in queries:
        print(f"\n> {q}")
        try:
            result = parser.execute(q)
            print(json.dumps(result, indent=2, default=str))
        except SQLTauError as e:
            print(f"[SQL-τ Error] {e}")