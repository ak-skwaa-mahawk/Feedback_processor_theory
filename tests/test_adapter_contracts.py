from __future__ import annotations
import os, sys, tempfile, sqlite3, time
import pytest

from fpt.events import ProjectionEvent, EventDispatcher, LedgerListener
from fpt.adapters import SovereignLedgerAdapter, TordialManifoldAdapter

def test_ledger_listener_protocol_conformance():
    """Verify adapters strictly inherit and implement LedgerListener."""
    assert issubclass(SovereignLedgerAdapter, LedgerListener)
    assert issubclass(TordialManifoldAdapter, LedgerListener)
    assert hasattr(SovereignLedgerAdapter, "on_projection")
    assert hasattr(TordialManifoldAdapter, "on_projection")

def test_external_repository_isolation():
    """Ensure fpt adapters never import external constellation packages."""
    import fpt.adapters as adapters_mod
    imported_modules = sys.modules.keys()
    
    # Assert neither external repository tree is imported in-process
    assert "tordial" not in imported_modules
    assert "human_in_the_loop" not in imported_modules
    assert "sovereign_ledger" not in imported_modules

def test_sovereign_ledger_adapter_contract():
    """Validate database write contract for SovereignLedgerAdapter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_ledger.db")
        adapter = SovereignLedgerAdapter(db_path=db_path)
        
        event = ProjectionEvent(
            task_id="CONTRACT-TEST-001",
            timestamp_ns=time.time_ns(),
            vector_dim=128,
            projection_norm=0.99995,
            shadow_energy=0.00042,
            action="CONTRACT_TEST_COMMIT",
            operator_signature="ED25519_CONTRACT_VALID",
            metadata={"source": "test_suite", "status": "verified"}
        )
        
        adapter.on_projection(event)
        
        # Verify SQLite schema conformance
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("""
                SELECT task_id, vector_dim, projection_norm, shadow_energy, action, operator_signature 
                FROM projection_records WHERE task_id = ?
            """, ("CONTRACT-TEST-001",)).fetchone()
            
            assert row is not None
            assert row[0] == "CONTRACT-TEST-001"
            assert row[1] == 128
            assert pytest.approx(row[2], rel=1e-4) == 0.99995
            assert pytest.approx(row[3], rel=1e-4) == 0.00042
            assert row[4] == "CONTRACT_TEST_COMMIT"
            assert row[5] == "ED25519_CONTRACT_VALID"

def test_tordial_manifold_adapter_contract():
    """Validate database write contract for TordialManifoldAdapter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_manifold.db")
        adapter = TordialManifoldAdapter(db_path=db_path)
        
        event = ProjectionEvent(
            task_id="MANIFOLD-CONTRACT-002",
            timestamp_ns=time.time_ns(),
            vector_dim=64,
            projection_norm=1.00000,
            shadow_energy=0.13769,
            action="MANIFOLD_STEP",
            operator_signature="NONE",
            metadata={}
        )
        
        adapter.on_projection(event)
        
        # Verify schema conformance
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("""
                SELECT vector_dim, norm, residual_energy 
                FROM manifold_telemetry WHERE vector_dim = ?
            """, (64,)).fetchone()
            
            assert row is not None
            assert row[0] == 64
            assert pytest.approx(row[1], rel=1e-4) == 1.00000
            assert pytest.approx(row[2], rel=1e-4) == 0.13769
