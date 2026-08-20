"""
async_projection_service.py
Asynchronous batch projection service integrating AsyncWorkerPool with OnlineProjectionMemory.
Enables concurrent batch updates, low-latency queries, and backpressure management.
"""
from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional
import numpy as np

from async_dispatch_pipeline import AsyncWorkerPool
from living_zero_projection import OnlineProjectionMemory


class AsyncProjectionService:
    def __init__(
        self,
        d: int = 64,
        max_patterns: int = 200,
        num_workers: int = 4,
        max_queue_size: int = 1000,
    ):
        self.d = d
        self.memory = OnlineProjectionMemory(d=d, max_patterns=max_patterns)
        self.pool = AsyncWorkerPool(num_workers=num_workers, max_queue_size=max_queue_size)
        self._lock = asyncio.Lock()

    def _handle_projection_task(self, payload: Dict[str, Any]):
        action = payload.get("action", "project")
        vector = np.array(payload["vector"], dtype=float)

        if action == "add":
            self.memory.add_pattern(vector)
        elif action == "revoke":
            pattern_id = payload["pattern_id"]
            self.memory.selective_revoke(pattern_id)
        elif action == "project":
            return self.memory.project(vector)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def start(self):
        await self.pool.start(handler=self._handle_projection_task)

    async def ingest_vector(self, task_id: str, vector: np.ndarray, action: str = "add", pattern_id: Optional[int] = None):
        payload = {"action": action, "vector": vector.tolist(), "pattern_id": pattern_id}
        await self.pool.submit(task_id=task_id, payload=payload)

    async def ingest_batch(self, batch_vectors: List[np.ndarray], action: str = "add"):
        batch = [
            {"id": f"batch_{idx}", "action": action, "vector": v.tolist()}
            for idx, v in enumerate(batch_vectors)
        ]
        await self.pool.submit_batch(batch)

    async def shutdown(self):
        await self.pool.shutdown()
