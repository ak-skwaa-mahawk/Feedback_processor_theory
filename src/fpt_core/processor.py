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