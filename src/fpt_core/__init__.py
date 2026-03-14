from __future__ import annotations

# Core exports
from .processor import FPTOmegaProcessor, FeedbackProcessor
from .models import FeedbackEvent, ResonanceResult
from .utils import process_single_event

__version__ = "0.1.0"

__all__ = [
    "FPTOmegaProcessor",
    "FeedbackProcessor",
    "FeedbackEvent",
    "ResonanceResult",
    "process_single_event",
]