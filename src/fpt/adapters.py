"""
fpt.adapters
SQLite persistence adapters implementing the LedgerListener protocol.
"""
from __future__ import annotations
import sqlite3
import json
from typing import Optional
from .events import ProjectionEvent, LedgerListener


class SovereignLedgerAdapter(LedgerListener):
    """Persists projection transactions and operator signatures to sovereign_ledger.db."""
    def __init__(self, db_path: str = "sovereign_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projection_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    timestamp_ns INTEGER,
                    vector_dim INTEGER,
                    projection_norm REAL,
                    shadow_energy REAL,
                    action TEXT,
                    operator_signature TEXT,
                    metadata_json TEXT
                )
            """)
            conn.commit()

    def on_projection(self, event: ProjectionEvent) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO projection_records (
                    task_id, timestamp_ns, vector_dim, projection_norm,
                    shadow_energy, action, operator_signature, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.task_id,
                    event.timestamp_ns,
                    event.vector_dim,
                    event.projection_norm,
                    event.shadow_energy,
                    event.action,
                    event.operator_signature,
                    json.dumps(event.metadata),
                )
            )
            conn.commit()


class TordialManifoldAdapter(LedgerListener):
    """Persists manifold state vectors and telemetry metrics to tordial_manifold.db."""
    def __init__(self, db_path: str = "tordial_manifold.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS manifold_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_ns INTEGER,
                    vector_dim INTEGER,
                    norm REAL,
                    residual_energy REAL
                )
            """)
            conn.commit()

    def on_projection(self, event: ProjectionEvent) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO manifold_telemetry (
                    timestamp_ns, vector_dim, norm, residual_energy
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    event.timestamp_ns,
                    event.vector_dim,
                    event.projection_norm,
                    event.shadow_energy,
                )
            )
            conn.commit()
