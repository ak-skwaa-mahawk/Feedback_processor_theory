from __future__ import annotations
import subprocess
import sys

def test_canonical_import_isolation():
    """Verify that src/fpt never imports non-canonical root or experimental modules."""
    res = subprocess.run([sys.executable, "scripts/enforce_canonical_boundary.py"], capture_output=True, text=True)
    assert res.returncode == 0, f"Boundary violation detected:\n{res.stdout}\n{res.stderr}"
