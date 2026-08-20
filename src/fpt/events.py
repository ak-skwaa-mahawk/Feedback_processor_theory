"""
fpt.events
Decoupled event interface for projection telemetry and ledger ingestion.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import runtime_checkable, Any, Dict, List, Optional, Protocol
import time


@dataclass(frozen=True)
class ProjectionEvent:
    timestamp_ns: int
    vector_dim: int
    projection_norm: float
    shadow_energy: float
    action: str = "encode"
    task_id: Optional[str] = None
    operator_signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LedgerListener(Protocol):
    def on_projection(self, event: ProjectionEvent) -> None:
        """Handle incoming projection event for ledger inscription or telemetry."""
        ...


class EventDispatcher:
    """Dispatches projection events to registered ledger adapters without blocking."""
    def __init__(self):
        self._listeners: List[LedgerListener] = []

    def register(self, listener: LedgerListener) -> None:
        self._listeners.append(listener)

    def dispatch(self, event: ProjectionEvent) -> None:
        for listener in self._listeners:
            listener.on_projection(event)
