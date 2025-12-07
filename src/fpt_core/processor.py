# src/fpt_core/processor.py
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime
from typing import Any

from .codex.loader import CodexLoader
from .engine import ResonanceEngine
from .cache import HarmonicCache
from .models import FeedbackEvent, ResonanceResult


class FeedbackProcessor:
    """
    Stateful processor for living resonance analysis.
    
    Maintains an immutable base codex while allowing ceremonial session overrides
    for contextual adaptation without compromising sovereignty.
    """

    def __init__(
        self,
        codex_mode: str = "default",
        root_inscription: str | None = None,
        /,
    ) -> None:
        # 1. Load the pristine, immutable base codex from bundled resources
        self._base_codex = CodexLoader.load(codex_mode)
        
        # 2. Create session-specific codex if ceremonial override is provided
        if root_inscription:
            self._session_codex = self._base_codex.clone_and_override(root_inscription)
        else:
            self._session_codex = self._base_codex
            
        # 3. Initialize the resonance engine with the session codex
        self._engine = ResonanceEngine(codex=self._session_codex)
        
        # 4. Initialize persistent harmonic cache for efficiency across events
        self._harmonic_cache = HarmonicCache()

    def process(self, event: FeedbackEvent) -> ResonanceResult:
        """Synchronous processing of a single feedback event."""
        return self._engine.analyze(event, cache=self._harmonic_cache)

    async def process_async(self, event: FeedbackEvent) -> ResonanceResult:
        """Asynchronous entry point – safe for high-throughput propagation layers."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, event)
# src/fpt_core/processor.py
class FeedbackProcessor:
    def __init__(
        self,
        codex_mode: str = "default",
        root_inscription: str | None = None,
        /,
    ) -> None:
        self._codex = CodexLoader.load(codex_mode)  # Immutable cultural/theoretical anchors
        if root_inscription:
            self._codex.override_root(root_inscription)  # Allows ceremonial override if needed
        self._engine = ResonanceEngine(codex=self._codex)
        self._harmonic_cache = HarmonicCache()

    def process(self, event: FeedbackEvent) -> ResonanceResult:
        return self._engine.analyze(event, cache=self._harmonic_cache)

    async def process_async(self, event: FeedbackEvent) -> ResonanceResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, event)