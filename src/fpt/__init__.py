"""
Feedback Processor Theory (FPT)
Deterministic orthogonal projections, async dispatch pipelines, and ledger persistence.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .events import ProjectionEvent, EventDispatcher
from .adapters import SovereignLedgerAdapter, TordialManifoldAdapter

# Canonical algebra & memory dynamics
from .algebra.living_zero_core import (
    normalize,
    OwnershipEncoder,
    OwnershipProjector,
    OwnershipMemory,
    CA3Dynamics,
    demo_small_run,
)
from .algebra.living_zero_projection import OnlineProjectionMemory

# Canonical runtime & worker services
from .runtime.async_dispatch_pipeline import AsyncWorkerPool, ProcessingTask
from .runtime.async_projection_service import AsyncProjectionService

__all__ = [
    "__version__",
    "ProjectionEvent",
    "EventDispatcher",
    "SovereignLedgerAdapter",
    "TordialManifoldAdapter",
    "normalize",
    "OwnershipEncoder",
    "OwnershipProjector",
    "OwnershipMemory",
    "CA3Dynamics",
    "OnlineProjectionMemory",
    "AsyncWorkerPool",
    "ProcessingTask",
    "AsyncProjectionService",
    "demo_small_run",
]
