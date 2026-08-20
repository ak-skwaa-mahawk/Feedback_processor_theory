import pytest
import time
from fpt.events import ProjectionEvent, EventDispatcher


class MockLedgerAdapter:
    def __init__(self):
        self.recorded_events = []

    def on_projection(self, event: ProjectionEvent) -> None:
        self.recorded_events.append(event)


def test_event_dispatch_flow():
    dispatcher = EventDispatcher()
    adapter = MockLedgerAdapter()
    dispatcher.register(adapter)

    event = ProjectionEvent(
        timestamp_ns=time.time_ns(),
        vector_dim=16,
        projection_norm=0.998,
        shadow_energy=0.015,
        action="encode",
        task_id="tx_001",
    )

    dispatcher.dispatch(event)

    assert len(adapter.recorded_events) == 1
    assert adapter.recorded_events[0].task_id == "tx_001"
    assert adapter.recorded_events[0].projection_norm == 0.998
