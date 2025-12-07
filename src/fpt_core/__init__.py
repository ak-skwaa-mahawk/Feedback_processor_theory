# src/fpt_core/__init__.py
from .models import FeedbackEvent, ResonanceResult
from .processor import FeedbackProcessor

__all__ = ["FeedbackProcessor", "process_single_event", "FeedbackEvent", "ResonanceResult"]

def process_single_event(
    event_data: dict,
    *,
    codex_mode: str = "default",
    root_inscription: str | None = None,
) -> ResonanceResult:
    """
    Stateless, high-level entry point for one-cycle resonance processing.
    Ideal for serverless, CLI, or simple propagation layers.
    """
    event = FeedbackEvent(**event_data)
    processor = FeedbackProcessor(codex_mode=codex_mode, root_inscription=root_inscription)
    return processor.process(event)