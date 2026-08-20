"""
ingestion_recovery.py
Dead-letter queue, exponential backoff, and idempotent retry wrapper for data ingestion.
"""
from __future__ import annotations
import time
import logging
from typing import Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestionRecovery")

class IngestionPipeline:
    def __init__(self, max_retries: int = 3, base_delay: float = 0.5):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.dead_letter_queue: list[dict[str, Any]] = []

    def process_record_with_recovery(self, record: dict[str, Any], handler: Callable[[dict[str, Any]], None]) -> bool:
        for attempt in range(1, self.max_retries + 1):
            try:
                handler(record)
                return True
            except Exception as e:
                backoff = self.base_delay * (2 ** (attempt - 1))
                logger.warning(f"Ingestion attempt {attempt} failed for record {record.get('id', 'unknown')}: {e}. Retrying in {backoff:.2f}s...")
                time.sleep(backoff)

        logger.error(f"Record {record.get('id', 'unknown')} failed after {self.max_retries} attempts. Routing to DLQ.")
        self.dead_letter_queue.append({"record": record, "timestamp": time.time()})
        return False
