from __future__ import annotations
from pathlib import Path
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .sorter import SortEngine

class SortEventHandler(FileSystemEventHandler):
    def __init__(self, engine: SortEngine):
        super().__init__()
        self.engine = engine

    def on_created(self, event):
        if event.is_directory:
            return
        self.engine.classify_and_move(Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        self.engine.classify_and_move(Path(event.dest_path))

    def on_modified(self, event):
        # Optional: re-check modified files
        if event.is_directory:
            return
        self.engine.classify_and_move(Path(event.src_path))

class WatchRunner:
    def __init__(self, engine: SortEngine):
        self.engine = engine
        self.observer = Observer()

    def run(self):
        handler = SortEventHandler(self.engine)
        self.observer.schedule(handler, str(self.engine.root), recursive=True)
        self.observer.start()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()