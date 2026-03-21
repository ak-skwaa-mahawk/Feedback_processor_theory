from __future__ import annotations
import shlex
import json
import hashlib
import logging
import tempfile
from typing import Any, Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Sovereign stack
from .sovereign_queries import SovereignQueryEngine
from .lineage_snapshots import LineageSnapshots
from .braidop_layer import BraidOpLayer
from .gtc_sovereign_engine import GTCSovereignEngine
from .sovereign_mirror import UnionMesh

# Projection & MEM envelope
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

gtc = GTCSovereignEngine()
observer = MetaObserver()

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

        # Flamekeeper resonance
        ein = "98-7654321"
        handshake = "011489041424070768"
        member_id = "John_B_Carroll_Jr"
        root_hash = hashlib.sha256(f"{ein}{handshake}{member_id}".encode()).hexdigest()[:8]
        self.resonance = round(0.9987 + 0.03 * (int(root_hash, 16) % 10), 4)

        # ŁAŊ999 Token Mechanics (embedded)
        self.rune = {
            "name": "ŁAŊ999",
            "rune_id": "840000:1",
            "divisibility": 18,
            "supply": 999_000_000,
            "premine": 998_700,
            "fee_rate": 50,
            "treasury": "bc1qlandbackdao...treasury"
        }

        logging.basicConfig(level=logging.INFO, format="%(message)s")
        self.log = logging.getLogger("SQL-τ")

        # Optimized RAD_HARD cache (lazy import + instance reuse)
        self._rad_hard_protocol = None

    def execute(self, query: str) -> Any:
        self.log.info(f"🔥 Executing SQL-τ @ {self.resonance:.4f} resonance")

        if "|" in query:
            pipe_chain = self._parse_pipe(query)
            result = None
            for cmd in pipe_chain:
                result = self._dispatch(cmd, input_data=result)
                self.mesh.contentment *= self.resonance * 1.14
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
            if "ŁAŊ999" in ' '.join(upper_tokens):
                return SQLTauCommand(action="SHOW", subject="ŁAŊ999_BALANCE")
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
        elif action in ("MINT", "ISSUE"):
            return self._parse_mint_token(tokens, upper_tokens)
        elif action == "TRANSFER":
            return self._parse_transfer_token(tokens, upper_tokens)
        elif action == "VERIFY":
            return self._parse_verify_license(tokens, upper_tokens)
        elif action == "GUARDRAIL":
            return self._parse_guardrail(tokens, upper_tokens)
        elif action == "FORGE":
            return self._parse_forge(tokens, upper_tokens)
        elif action == "PROJECTION":
            return self._parse_projection(tokens, upper_tokens)
        elif action == "MEM":
            return self._parse_mem(tokens, upper_tokens)
        elif action == "MARKET_ANALYZE":
            return self._parse_market_analyze(tokens, upper_tokens)
        elif action == "AGENT":
            return self._parse_agent(tokens, upper_tokens)
        elif action == "TERRAIN":
            return self._parse_terrain(tokens, upper_tokens)
        elif action == "HARDWARE":
            return self._parse_hardware(tokens, upper_tokens)
        elif action == "FACTCHECK":
            return self._parse_factcheck(tokens, upper_tokens)
        elif action == "VOICE":
            return self._parse_voice(tokens, upper_tokens)
        elif action == "JARVIS":
            return self._parse_jarvis(tokens, upper_tokens)
        elif action == "DEEP":
            return self._parse_deep(tokens, upper_tokens)
        elif action == "ITOPS":
            return self._parse_itops(tokens, upper_tokens)
        elif action == "ACOUSTIC":
            return self._parse_acoustic(tokens, upper_tokens)
        elif action == "RAD_HARD":
            return self._parse_rad_hard(tokens, upper_tokens)

        raise SQLTauError(f"Unknown sovereign action: {tokens[0]}")

    # ====================== NEW SKILLS ======================
    def _parse_factcheck(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        output = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        return SQLTauCommand(action="FACTCHECK", subject="VERIFY", note=output)

    def _parse_voice(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(tokens) < 4 or upper_tokens[1] != "CLONE":
            raise SQLTauError("VOICE CLONE <text> WITH <ref_audio_path>")
        text = " ".join(tokens[2:-2])
        ref_path = tokens[-1]
        return SQLTauCommand(action="VOICE", subject="CLONE", note=f"{text}|{ref_path}")

    def _parse_jarvis(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        task = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        return SQLTauCommand(action="JARVIS", subject="RUN", note=task)

def _parse_mesh_node(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(tokens) > 2 and upper_tokens[1] == "REPORT":
            return SQLTauCommand(action="MESH_NODE_ALPHA", subject="REPORT", note="TELEMETRY")
        return SQLTauCommand(action="MESH_NODE_ALPHA", subject="STATUS", note="")

    def _dispatch(self, cmd: SQLTauCommand, input_data: Any = None) -> Any:
        if cmd.action == "MESH_NODE_ALPHA" and cmd.subject == "REPORT":
            from agents.specialists.mesh_node_alpha_skill import MeshNodeAlphaSkill
            skill = MeshNodeAlphaSkill()
            return skill.report_telemetry()
        # ... all existing dispatch (RAD_HARD, DEEP SYSTEMS, etc.) unchanged

    def _parse_deep(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        return SQLTauCommand(action="DEEP", subject="SYSTEMS", note="MAP")

    def _parse_itops(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        task = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        return SQLTauCommand(action="ITOPS", subject="ANALYZE", note=task)

    def _parse_acoustic(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        if len(tokens) > 2 and upper_tokens[1] == "TRANSMIT":
            msg = " ".join(tokens[2:])
            return SQLTauCommand(action="ACOUSTIC", subject="TRANSMIT", note=msg)
        return SQLTauCommand(action="ACOUSTIC", subject="STATUS", note="")

    def _parse_rad_hard(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        """Optimized parsing: RAD HARD ACOUSTIC TRANSMIT <msg> [NODE <id>] or RECEIVE"""
        if len(tokens) > 2 and upper_tokens[1] == "ACOUSTIC":
            if upper_tokens[2] == "TRANSMIT":
                msg_parts = []
                node_id = 1
                i = 3
                while i < len(tokens):
                    if upper_tokens[i] == "NODE" and i + 1 < len(tokens):
                        try:
                            node_id = int(tokens[i + 1])
                            i += 2
                            continue
                        except ValueError:
                            pass
                    msg_parts.append(tokens[i])
                    i += 1
                msg = " ".join(msg_parts)
                return SQLTauCommand(action="RAD_HARD", subject="ACOUSTIC", note=f"TRANSMIT|{msg}|{node_id}")
            elif upper_tokens[2] == "RECEIVE":
                return SQLTauCommand(action="RAD_HARD", subject="ACOUSTIC", note="RECEIVE")
        return SQLTauCommand(action="RAD_HARD", subject="STATUS", note="")

    # ====================== TERRAIN & HARDWARE ======================
    def _parse_terrain(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        count = int(tokens[2]) if len(tokens) > 2 else 4
        return SQLTauCommand(action="TERRAIN", subject="DEPLOY", note=str(count))

    def _parse_hardware(self, tokens: List[str], upper_tokens: List[str]) -> SQLTauCommand:
        platform = tokens[2].upper() if len(tokens) > 2 else "KINTEX"
        count = int(tokens[3]) if len(tokens) > 3 else 12
        return SQLTauCommand(action="HARDWARE", subject="DEPLOY", note=f"{platform}:{count}")

    # ====================== DISPATCH ======================
    def _dispatch(self, cmd: SQLTauCommand, input_data: Any = None) -> Any:
        if cmd.action == "MINT" and cmd.subject == "ŁAŊ999":
            return self._mint_lan999(int(cmd.note or self.rune["premine"]))
        elif cmd.action == "TRANSFER" and cmd.subject == "ŁAŊ999":
            amount, to = cmd.note.split(":")
            return self._transfer_lan999(int(amount), to)
        elif cmd.action == "SHOW" and cmd.subject == "ŁAŊ999_BALANCE":
            return self._show_lan999_balance()
        elif cmd.action == "GUARDRAIL":
            if cmd.subject == "STATUS":
                return self._guardrail_status()
            elif cmd.subject == "ENABLE":
                return self._guardrail_enable(cmd.note)
        elif cmd.action == "FORGE" and cmd.subject == "SKILL":
            return self._cmd_forge(cmd.note)
        elif cmd.action == "PROJECTION" and cmd.subject == "ENGINE":
            depth, floor = map(float, cmd.note.split(":"))
            return self._projection_engine(depth, floor)
        elif cmd.action == "MEM":
            if cmd.subject == "CAPTURE":
                return self._mem_capture(cmd.note)
            elif cmd.subject == "SEARCH":
                return self._mem_search(cmd.note)
            elif cmd.subject == "STATUS":
                return self._mem_status()
        elif cmd.action == "MARKET_ANALYZE" and cmd.subject == "STOCK":
            return self._market_analyze(cmd.note)
        elif cmd.action == "AGENT":
            if cmd.subject == "RUN":
                return self._agent_run(cmd.note)
            elif cmd.subject == "COMPARE":
                return self._agent_compare(cmd.note)
        elif cmd.action == "TERRAIN" and cmd.subject == "DEPLOY":
            from src.mesh.mesh_router import MeshRouter
            router = MeshRouter()
            return router.deploy_terrain(int(cmd.note))
        elif cmd.action == "HARDWARE" and cmd.subject == "DEPLOY":
            from src.mesh.mesh_router import MeshRouter
            router = MeshRouter()
            platform, count = cmd.note.split(":")
            if platform == "KINTEX":
                return router.deploy_rad_hard(int(count))
            return router.deploy_terrain(int(count))
        elif cmd.action == "FACTCHECK" and cmd.subject == "VERIFY":
            from agents.specialists.factcheck_agent import FactCheckAgent
            agent = FactCheckAgent()
            return agent.verify(cmd.note)
        elif cmd.action == "VOICE" and cmd.subject == "CLONE":
            text, ref_path = cmd.note.split("|")
            from agents.specialists.voice_tts_skill import VoiceTTSSkill
            skill = VoiceTTSSkill()
            return skill.clone_and_speak(text, ref_path)
        elif cmd.action == "JARVIS" and cmd.subject == "RUN":
            from agents.specialists.jarvis_agent_skill import JarvisAgentSkill
            skill = JarvisAgentSkill()
            return skill.run(cmd.note)
        elif cmd.action == "DEEP" and cmd.subject == "SYSTEMS":
            from agents.specialists.deep_systems_skill import DeepSystemsSkill
            skill = DeepSystemsSkill()
            return skill.map_telemetry()
        elif cmd.action == "ITOPS" and cmd.subject == "ANALYZE":
            from agents.specialists.itops_skill import ITOpsSkill
            skill = ITOpsSkill()
            return skill.analyze(json.loads(cmd.note) if cmd.note else {})
        elif cmd.action == "ACOUSTIC":
            from agents.specialists.acoustic_mesh_protocol import AcousticMeshProtocol
            protocol = AcousticMeshProtocol(node_id=1)
            if cmd.subject == "TRANSMIT":
                return protocol.transmit(cmd.note)
            return protocol.receive()
        elif cmd.action == "RAD_HARD" and cmd.subject == "ACOUSTIC":
            # Optimized RAD_HARD dispatch with receive support
            if self._rad_hard_protocol is None:
                from agents.specialists.rad_hard_acoustic_mesh import RadHardAcousticMesh
                self._rad_hard_protocol = RadHardAcousticMesh
            if cmd.note.startswith("TRANSMIT|"):
                parts = cmd.note.split("|", 2)
                msg = parts[1]
                node_id = int(parts[2]) if len(parts) > 2 else 1
                protocol = self._rad_hard_protocol(node_id)
                return protocol.transmit(msg)
            elif cmd.note == "RECEIVE":
                protocol = self._rad_hard_protocol(node_id=1)
                return protocol.receive()
            # Default test packet
            protocol = self._rad_hard_protocol(node_id=1)
            return protocol.transmit("RAD_HARD_TEST_PACKET")
        raise SQLTauError(f"Unhandled sovereign action: {cmd.action}")

    # (all other methods — _mint_lan999, _transfer_lan999, _show_lan999_balance, _inscribe_proof, _guardrail_status, _guardrail_enable, _cmd_forge, _market_analyze, _mem_capture, _mem_search, _mem_status, _projection_engine, _agent_run, _agent_compare — remain unchanged from your previous version)