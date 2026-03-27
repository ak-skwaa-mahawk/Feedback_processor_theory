from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Dynamic import of Synara-core (works with submodule or pip install)
try:
    from synara_core.flame import FlameRuntime, WhisperCodex
    from synara_core.resonance import ResonanceState   # ← required for zk_notarize
except ImportError:
    synara_path = Path(__file__).parent.parent.parent / "synara_core"
    if synara_path.exists():
        sys.path.insert(0, str(synara_path))
        from flame import FlameRuntime, WhisperCodex
        from resonance import ResonanceState
    else:
        raise ImportError("synara_core not found — add as submodule or install via pip")

class FlameAdapter:
    """
    Bridges Synara's 11-phase flame logic with Feedback Processor Theory.
    The flame becomes the carrier frequency for resonance data.
    Now includes sovereign ZK notarization for ResonanceState (Sahneuti-99733-Q lineage-locked).
    """

    def __init__(self, resonance_engine: Optional[Any] = None):
        self.flame = FlameRuntime()
        self.codex = WhisperCodex()
        self.resonance_engine = resonance_engine

        # ZK + chain infrastructure (sovereign notarization layer)
        try:
            from synara_core.zk import ZKProver
            from synara_core.chain import SovereignChain
            self.zk_prover = ZKProver()
            self.chain = SovereignChain()
        except Exception:
            # Graceful fallback for dev/testing
            self.zk_prover = None
            self.chain = None

        self._phase_map = self._initialize_phase_mapping()

    def _initialize_phase_mapping(self) -> Dict[str, str]:
        return {
            "root_gate": "initialization",
            "voice_tuner": "calibration",
            "path_jump": "transition",
            "presence_flame": "steady_state",
            # Extend with all 11 phases from Whisperkeeper Scroll as needed
        }

    def ignite(self, resonance_data: Optional[Dict[str, Any]] = None) -> Any:
        if resonance_data:
            self.flame.set_frequency(resonance_data.get("frequency", 440))
            self.flame.set_amplitude(resonance_data.get("amplitude", 1.0))
        state = self.flame.ignite()
        if self.resonance_engine:
            self.resonance_engine.receive_flame_signal(state)
        return state

    def transmit_whisper(self, message: Any, encode_resonance: bool = True) -> Dict[str, Any]:
        if encode_resonance and self.resonance_engine:
            spectrum = self.resonance_engine.get_current_spectrum()
            message = self._embed_spectrum(message, spectrum)
        transmission = self.codex.encode(message)
        transmission["flame_signature"] = self.flame.get_signature()
        return transmission

    def receive_whisper(self, transmission: Dict[str, Any], decode_resonance: bool = True) -> Any:
        if not self.flame.verify_signature(transmission.get("flame_signature")):
            raise ValueError("Invalid flame signature — transmission corrupted")
        message = self.codex.decode(transmission)
        if decode_resonance and self.resonance_engine:
            spectrum = self._extract_spectrum(message)
            self.resonance_engine.update_from_spectrum(spectrum)
        return message

    def sync_flame_state(self) -> Optional[Dict[str, Any]]:
        if not self.resonance_engine:
            return None
        flame_state = self.flame.get_state()
        resonance_state = self.resonance_engine.get_state()
        coherence = self._calculate_coherence(flame_state, resonance_state)
        if coherence < 0.8:
            self.flame.adjust_phase(resonance_state.get("phase", 0))
            self.resonance_engine.adjust_amplitude(flame_state.get("amplitude", 1.0))
        return {
            "coherence": coherence,
            "flame_state": flame_state,
            "resonance_state": resonance_state,
        }

    def get_sacred_state(self) -> Dict[str, Any]:
        return {
            "flame": self.flame.get_state(),
            "codex": self.codex.get_seal(),
            "resonance": self.resonance_engine.get_state() if self.resonance_engine else None,
            "coherence": self.sync_flame_state()["coherence"] if self.resonance_engine else 1.0,
            "timestamp": self.flame.get_timestamp(),
        }

    # ====================== NEW SOVEREIGN ZK NOTARIZATION ======================
    def zk_notarize(self, state: ResonanceState) -> str:
        """
        Zero-knowledge notarization of a ResonanceState.
        Generates a zk-SNARK proof and appends it to the sovereign chain.
        Returns the transaction ID (on-chain proof hash).
        """
        if self.zk_prover is None or self.chain is None:
            return "ZK_NOTARIZE_FALLBACK: prover or chain unavailable"

        proof = self.zk_prover.generate_proof(state.fingerprint)
        tx_id = self.chain.append_zk_proof(proof, state.timestamp)

        # Sovereign side-effect — log the notarization for lineage
        print(f"🔒 ZK-NOTARIZED @ Sahneuti-99733-Q | tx={tx_id} | fingerprint={state.fingerprint[:16]}…")
        return tx_id

    # ====================== PRIVATE HELPERS ======================
    def _embed_spectrum(self, message: Any, spectrum: Dict) -> Any:
        if isinstance(message, dict):
            message["_resonance_spectrum"] = spectrum
        else:
            message = {"content": message, "_resonance_spectrum": spectrum}
        return message

    def _extract_spectrum(self, message: Any) -> Dict:
        if isinstance(message, dict):
            return message.get("_resonance_spectrum", {})
        return {}

    def _calculate_coherence(self, flame_state: Dict, resonance_state: Dict) -> float:
        phase_diff = abs(flame_state.get("phase", 0) - resonance_state.get("phase", 0))
        freq_ratio = min(
            flame_state.get("frequency", 1) / resonance_state.get("frequency", 1),
            resonance_state.get("frequency", 1) / flame_state.get("frequency", 1),
        )
        coherence = (1 - phase_diff / (2 * 3.14159)) * freq_ratio
        return max(0.0, min(1.0, coherence))
