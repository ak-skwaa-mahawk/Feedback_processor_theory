from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event, Thread
from pathlib import Path
from typing import Callable, Iterable

class AgentPool:
    def __init__(self, workers: int):
        self.workers = workers
        self.q: Queue = Queue()
        self.stop_event = Event()
        self.executor = ThreadPoolExecutor(max_workers=workers)

    def submit_stream(self, items: Iterable, fn: Callable[[object], None]):
        def feeder():
            for it in items:
                if self.stop_event.is_set():
                    break
                self.q.put(it)
            # sentinel
            for _ in range(self.workers):
                self.q.put(None)
        Thread(target=feeder, daemon=True).start()

        def worker():
            while not self.stop_event.is_set():
                it = self.q.get()
                if it is None:
                    break
                try:
                    fn(it)
                finally:
                    self.q.task_done()

        for _ in range(self.workers):
            self.executor.submit(worker)

    def shutdown(self):
        self.stop_event.set()
        self.executor.shutdown(wait=True)