"""
async_dispatch_pipeline.py
Asynchronous worker pool and task dispatcher for Feedback Processor Theory.
Supports batch chunking, concurrent processing, backpressure, and DLQ routing.
"""
from __future__ import annotations
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ingestion_recovery import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AsyncDispatcher")


@dataclass
class ProcessingTask:
    task_id: str
    payload: Dict[str, Any]
    retries: int = 0
    created_at: float = field(default_factory=time.time)


class AsyncWorkerPool:
    def __init__(
        self,
        num_workers: int = 4,
        max_queue_size: int = 1000,
        max_retries: int = 3,
        base_backoff: float = 0.05,
    ):
        self.num_workers = num_workers
        self.queue: asyncio.Queue[Optional[ProcessingTask]] = asyncio.Queue(maxsize=max_queue_size)
        self.recovery = IngestionPipeline(max_retries=max_retries, base_delay=base_backoff)
        self.workers: List[asyncio.Task] = []
        self._is_running = False

    async def _worker_loop(self, worker_id: int, handler: Callable[[Dict[str, Any]], Any]):
        logger.info(f"Worker-{worker_id} started.")
        while self._is_running:
            task = await self.queue.get()
            if task is None:
                self.queue.task_done()
                break

            try:
                success = self.recovery.process_record_with_recovery(
                    record={"id": task.task_id, "data": task.payload},
                    handler=lambda r: handler(r["data"]),
                )
                if not success:
                    logger.warning(f"Worker-{worker_id}: Task {task.task_id} routed to DLQ.")
            except Exception as exc:
                logger.error(f"Worker-{worker_id}: Unhandled exception processing {task.task_id}: {exc}")
            finally:
                self.queue.task_done()

        logger.info(f"Worker-{worker_id} shutdown.")

    async def start(self, handler: Callable[[Dict[str, Any]], Any]):
        self._is_running = True
        self.workers = [
            asyncio.create_task(self._worker_loop(i, handler))
            for i in range(self.num_workers)
        ]

    async def submit(self, task_id: str, payload: Dict[str, Any]):
        task = ProcessingTask(task_id=task_id, payload=payload)
        await self.queue.put(task)

    async def submit_batch(self, batch: List[Dict[str, Any]]):
        for item in batch:
            task_id = item.get("id", f"task_{time.time_ns()}")
            await self.submit(task_id=task_id, payload=item)

    async def shutdown(self):
        await self.queue.join()
        self._is_running = False
        for _ in range(self.num_workers):
            await self.queue.put(None)
        await asyncio.gather(*self.workers)
        logger.info("Worker pool gracefully stopped.")
