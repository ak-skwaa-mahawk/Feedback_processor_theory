"""
Feedback Processor Theory (FPT)
Deterministic orthogonal projections, async dispatch pipelines, and ledger persistence.
"""
from __future__ import annotations

__version__ = "0.1.0"

from fpt.events import ProjectionEvent, EventDispatcher
from fpt.adapters import SovereignLedgerAdapter, TordialManifoldAdapter

# Optional fallback for local dev environment
try:
    from living_zero_core import *
except ImportError:
    pass

__all__ = [
    "__version__",
    "ProjectionEvent",
    "EventDispatcher",
    "SovereignLedgerAdapter",
    "TordialManifoldAdapter",
]
