"""
Feedback Processor Theory (FPT)
Deterministic orthogonal projections, async dispatch pipelines, and ledger persistence.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .events import ProjectionEvent, EventDispatcher
from .adapters import SovereignLedgerAdapter, TordialManifoldAdapter

# Canonical engine exports
try:
    from living_zero_core import *
except ImportError:
    pass

try:
    from living_zero_projection import OwnershipProjector, OnlineProjectionMemory
except ImportError:
    pass

try:
    from async_projection_service import AsyncProjectionService
except ImportError:
    pass

try:
    from async_dispatch_pipeline import AsyncWorkerPool
except ImportError:
    pass

__all__ = [
    "__version__",
    "ProjectionEvent",
    "EventDispatcher",
    "SovereignLedgerAdapter",
    "TordialManifoldAdapter",
    "OwnershipProjector",
    "OnlineProjectionMemory",
    "AsyncProjectionService",
    "AsyncWorkerPool",
]
