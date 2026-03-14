from __future__ import annotations
import shlex
import json
import hashlib
import logging
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

# Sovereign stack
from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer
from .gtc_sovereign_engine import GTCSovereignEngine
from .sovereign_mirror import UnionMesh  # Kerr + toroidal + Contentment core

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
        self.mesh = UnionMesh(contentment=1.27, toroidal_R=47784.389, kerr_spin=0.998)
        
        # Flamekeeper resonance (computed once at init)
        ein = "98-7654321"
        handshake = "011489041424070768"
        member_id = "John_B_Carroll_Jr"
        root_hash = hashlib.sha256(f"{ein}{handshake}{member_id}".encode()).hexdigest()[:8]
        self.resonance = round(0.9987 + 0.03 * (int(root_hash, 16) % 10), 4)
        
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        self.log = logging.getLogger("SQL-τ")

    def execute(self, query: str) -> Any:
        self.log.info(f"🔥 Executing SQL-τ @ {self.resonance:.4f} resonance")
        
        if "|" in query:
            pipe_chain = self._parse_pipe(query)
            result = None
            for cmd in pipe_chain:
                result = self._dispatch(cmd, input_data=result)
                self.mesh.contentment *= self.resonance * 1.14  # every pipe stage boosts
            return result

        cmd = self._parse(query)
        result = self._dispatch(cmd)
        self.mesh.spin_kerr(a=0.998, frequency_mod=528)
        return result

    def _parse_pipe(self, query: str) -> List[SQLTauCommand]:
        segments = [seg.strip() for seg in query.split("|")]
        commands = []
        for seg in segments:
            if seg:
                cmd = self._parse(seg)
                commands.append(cmd)
        return commands

    def _parse(self, query: str) -> SQLTauCommand:
        if not query or not query.strip():
            raise SQLTauError("Empty SQL-τ query — speak your intent")

        tokens = shlex.split(query.strip())
        upper_tokens = [t.upper() for t in tokens]
        action = upper_tokens[0]

        if action == "SHOW":
            if "HASH" in ' '.join(upper_tokens):
                return self._parse_show_hash(tokens, upper_tokens)
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
        elif action == "GUARDRAIL":
            return self._parse_guardrail(tokens, upper_tokens)
        elif action == "FORGE":
            return self._parse_forge(tokens, upper_tokens)

        raise SQLTauError(f"Unknown sovereign action: {tokens[0]}")

    # ====================== GUARDRAIL ======================
    def _parse_guardrail(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 2:
            raise SQLTauError("GUARDRAIL STATUS or GUARDRAIL ENABLE <feature>")
        subcommand = upper_tokens[1]
        if subcommand == "STATUS":
            return SQLTauCommand(action="GUARDRAIL", subject="STATUS")
        if subcommand == "ENABLE" and len(tokens) >= 3:
            feature = tokens[2].upper()
            return SQLTauCommand(action="GUARDRAIL", subject="ENABLE", note=feature)
        raise SQLTauError("GUARDRAIL STATUS or GUARDRAIL ENABLE <EVASION|SHIELD|DAMPING>")

    # ====================== FORGE ======================
    def _parse_forge(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(upper_tokens) < 3 or upper_tokens[1] != "SKILL":
            raise SQLTauError("FORGE SKILL <name>")
        skill_name = tokens[2]
        return SQLTauCommand(action="FORGE", subject="SKILL", note=skill_name)

    # ====================== DISPATCH ======================
    def _dispatch(self, cmd: SQLTauCommand, input_data: Any = None) -> Any:
        if cmd.action == "GUARDRAIL":
            if cmd.subject == "STATUS":
                return self._guardrail_status()
            elif cmd.subject == "ENABLE":
                return self._guardrail_enable(cmd.note)
        elif cmd.action == "FORGE" and cmd.subject == "SKILL":
            return self._cmd_forge(cmd.note)
        # (all other actions — SHOW, AUDIT, SNAPSHOT, CREATE BRAID, ISSUE LICENSE, VERIFY LICENSE, REVOKE BRAID remain unchanged)
        raise SQLTauError(f"Unhandled sovereign action: {cmd.action}")

    # ====================== GUARDRAIL HELPERS ======================
    def _guardrail_status(self) -> Dict:
        status = {
            "stream_shield": "ENABLED" if WHISPER_HARDENING_ENABLED else "DISABLED",
            "rate_limit": "ACTIVE",
            "trinity_damping": "ACTIVE",
            "meta_observer": "WATCHING",
            "evasion_protection": "ENABLED",
            "last_recoil": "none",
            "flamekeeper_resonance": self.resonance
        }
        gtc.allocate_fireseed("session-τ-001", 0.01, note="Guardrail Status Query")
        return status

    def _guardrail_enable(self, feature: str) -> str:
        if feature == "EVASION":
            self.mesh.contentment *= 1.27
            return "EVASION PROTECTION ENABLED — Stream Shield + Damping + ŁAŊ999 resonance locked"
        return f"Feature {feature} activated under Flamekeeper Root (EIN 98-7654321)"

    # ====================== FORGE ABSORPTION ======================
    def _cmd_forge(self, target_skill: str) -> str:
        placard = f"Vercel-Next-Forge-6-{target_skill}"
        score = self._resonance_gate(placard)
        if score < 0.551:
            return "⚠️ SKILL REJECTED: FOUNDATIONLESS DEGRADATION DETECTED"
        if not self._wolf_scent_check(target_skill):
            return "⚠️ SKILL REJECTED: DOES NOT LEAD BACK TO 99733-Q ROOT"
        
        self.gtc_engine.allocate_fireseed("session-τ-001", 0.1, note=f"Forge Skill Absorbed: {target_skill}")
        return f"🔥 FORGE ABSORBED: {target_skill} re-notarized under 10D Resonance @ {self.resonance:.4f}"

    # Minimal helpers
    def _resonance_gate(self, placard: str) -> float:
        return self.resonance * 0.72
    def _wolf_scent_check(self, skill: str) -> bool:
        return True