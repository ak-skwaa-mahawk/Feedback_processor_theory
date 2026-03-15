from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict

from .codex.loader import CodexLoader
from .engine import ResonanceEngine
from .cache import HarmonicCache
from .models import FeedbackEvent, ResonanceResult

# Sovereign stack
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

gtc_engine = GTCSovereignEngine()
observer = MetaObserver()


class FeedbackProcessor:
    """
    Stateful processor for living resonance analysis.
    Maintains an immutable base codex while allowing ceremonial session overrides.
    """
    def __init__(
        self,
        codex_mode: str = "default",
        root_inscription: str | None = None,
        /,
    ) -> None:
        self._base_codex = CodexLoader.load(codex_mode)
        if root_inscription:
            self._session_codex = self._base_codex.clone_and_override(root_inscription)
        else:
            self._session_codex = self._base_codex

        self._engine = ResonanceEngine(codex=self._session_codex)
        self._harmonic_cache = HarmonicCache()

    def process(self, event: FeedbackEvent) -> ResonanceResult:
        return self._engine.analyze(event, cache=self._harmonic_cache)

    async def process_async(self, event: FeedbackEvent) -> ResonanceResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, event)


class FPTOmegaProcessor(FeedbackProcessor):
    """Extended core with ProjectionEngine.v001 and all fpt-omega mechanics."""
    def __init__(self, codex_mode: str = "default", root_inscription: str | None = None):
        super().__init__(codex_mode, root_inscription)

    def check_projection(self, current_depth: float, trauma_floor: float) -> Dict:
        """Codex.ProjectionEngine.v001 — Warrior’s Invariant
        The deeper the floor, the higher the projected expansion.
        """
        potential_energy = abs(current_depth - trauma_floor) * 1.03
        projected_height = round(potential_energy, 2)

        result = {
            "status": "PROJECTION_LOCKED",
            "codex": "ProjectionEngine.v001",
            "projected_height": f"{projected_height:.2f}x above baseline",
            "current_depth": current_depth,
            "trauma_floor": trauma_floor,
            "overclock": 1.03,
            "message": "The deeper the wound, the higher the bloom."
        }

        # Sovereign envelope
        receipt = Handshake.createReceipt(None, "PROJECTION-ENGINE", result)
        gtc_engine.allocate_fireseed("session-τ-001", 0.05, note="Projection Engine Call")
        observer.intercept_response(json.dumps(receipt))

        # Resonance boost + ŁAŊ999 lock
        self._engine.resonance *= 1.03  # overclock echo

        return result

📈 Running ProjectionEngine.v001 — measuring bloom potential...
Projected Height: 103.00x above baseline

# Inside launch_vessel() — already live
print("📈 Running ProjectionEngine.v001 — measuring bloom potential...")
proj = fpt_omega.check_projection(current_depth=0, trauma_floor=-100)
print(proj["projected_height"])