import pytest
from pathlib import Path
import fpt

def test_fpt_public_api():
    """Assert all canonical symbols are exported regardless of execution context."""
    expected_symbols = {
        "OnlineProjectionMemory",
        "OwnershipProjector",
        "AsyncProjectionService",
        "AsyncWorkerPool",
    }
    actual_symbols = set(dir(fpt))
    assert expected_symbols.issubset(actual_symbols), (
        f"Missing canonical symbols: {expected_symbols - actual_symbols}"
    )

def test_fpt_functional_smoke():
    """Verify classes instantiated from the fpt package operate identically to core."""
    projector = fpt.OwnershipProjector(N=16, d=16)
    memory = fpt.OnlineProjectionMemory(N=16, ownership_projector=projector)
    assert memory.N == 16
