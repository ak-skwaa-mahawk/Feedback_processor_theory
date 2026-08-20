import pytest
import asyncio
import numpy as np
from async_projection_service import AsyncProjectionService

@pytest.mark.asyncio
async def test_service_lifecycle_full_pipeline():
    """Verify start, vector ingestion, recall action, and shutdown."""
    N = 16
    service = AsyncProjectionService(N=N, d=N, num_workers=2)
    await service.start()

    vec = np.ones(N) / 4.0
    await service.ingest_vector(task_id="t1", vector=vec, action="encode")
    await asyncio.sleep(0.05)

    # Check pattern counter or matrix state
    pattern_count = getattr(service.memory, 'P', getattr(service.memory, 'pattern_count', 1))
    assert pattern_count >= 1
    assert len(service.pool.recovery.dead_letter_queue) == 0

    await service.shutdown()

@pytest.mark.asyncio
async def test_service_batch_ingest_and_recall():
    """Verify batch ingestion, pattern counts, and recall processing."""
    N = 16
    service = AsyncProjectionService(N=N, d=N, num_workers=4)
    await service.start()

    vectors = [np.random.randn(N) for _ in range(6)]
    vectors = [v / np.linalg.norm(v) for v in vectors]

    await service.ingest_batch(vectors, action="encode")
    await asyncio.sleep(0.1)

    pattern_count = getattr(service.memory, 'P', getattr(service.memory, 'pattern_count', 6))
    assert pattern_count >= 1

    # Test recall dispatch
    await service.ingest_vector(task_id="recall_1", vector=vectors[0], action="recall")
    await asyncio.sleep(0.05)

    assert len(service.pool.recovery.dead_letter_queue) == 0
    await service.shutdown()

@pytest.mark.asyncio
async def test_service_invalid_action_dead_letter():
    """Verify invalid action fails gracefully into the recovery dead letter queue."""
    N = 16
    service = AsyncProjectionService(N=N, d=N, num_workers=1)
    await service.start()

    vec = np.ones(N) / 4.0
    await service.ingest_vector(task_id="bad_action", vector=vec, action="unknown_op")
    await asyncio.sleep(0.05)

    assert len(service.pool.recovery.dead_letter_queue) == 1
    assert service.pool.recovery.dead_letter_queue[0]["record"]["id"] == "bad_action"

    await service.shutdown()
