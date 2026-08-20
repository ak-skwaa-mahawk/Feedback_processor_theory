import os
import time
import tempfile
import sqlite3
import pytest
from fpt.events import ProjectionEvent, EventDispatcher
from fpt.adapters import SovereignLedgerAdapter, TordialManifoldAdapter


def test_sovereign_ledger_adapter_writes():
    with tempfile.TemporaryDirectory() as tmp:
        db_file = os.path.join(tmp, "test_sovereign.db")
        adapter = SovereignLedgerAdapter(db_path=db_file)
        
        event = ProjectionEvent(
            timestamp_ns=time.time_ns(),
            vector_dim=16,
            projection_norm=0.9991,
            shadow_energy=0.005,
            action="encode",
            task_id="task_sov_01",
            operator_signature="sig_99733_q",
            metadata={"source": "test_harness"}
        )
        adapter.on_projection(event)

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT task_id, projection_norm, operator_signature FROM projection_records")
            row = cursor.fetchone()

        assert row is not None
        assert row[0] == "task_sov_01"
        assert abs(row[1] - 0.9991) < 1e-4
        assert row[2] == "sig_99733_q"


def test_tordial_manifold_adapter_writes():
    with tempfile.TemporaryDirectory() as tmp:
        db_file = os.path.join(tmp, "test_tordial.db")
        adapter = TordialManifoldAdapter(db_path=db_file)

        event = ProjectionEvent(
            timestamp_ns=time.time_ns(),
            vector_dim=32,
            projection_norm=1.0000,
            shadow_energy=0.0000,
        )
        adapter.on_projection(event)

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT vector_dim, norm, residual_energy FROM manifold_telemetry")
            row = cursor.fetchone()

        assert row is not None
        assert row[0] == 32
        assert row[1] == 1.0000
        assert row[2] == 0.0000


def test_event_dispatcher_multi_adapter_fanout():
    with tempfile.TemporaryDirectory() as tmp:
        sov_db = os.path.join(tmp, "sov.db")
        tor_db = os.path.join(tmp, "tor.db")

        dispatcher = EventDispatcher()
        dispatcher.register(SovereignLedgerAdapter(db_path=sov_db))
        dispatcher.register(TordialManifoldAdapter(db_path=tor_db))

        event = ProjectionEvent(
            timestamp_ns=time.time_ns(),
            vector_dim=16,
            projection_norm=0.995,
            shadow_energy=0.01,
            task_id="fanout_01"
        )
        dispatcher.dispatch(event)

        with sqlite3.connect(sov_db) as conn:
            count_sov = conn.execute("SELECT COUNT(*) FROM projection_records").fetchone()[0]
        with sqlite3.connect(tor_db) as conn:
            count_tor = conn.execute("SELECT COUNT(*) FROM manifold_telemetry").fetchone()[0]

        assert count_sov == 1
        assert count_tor == 1
