"""
Legacy Compatibility Shim for FPT Root Namespace.
Canonical implementation strictly lives under `src/fpt/`.
"""
import sys
from pathlib import Path

# Ensure src/ is in sys.path if not installed in site-packages
_src_path = str(Path(__file__).resolve().parent.parent / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from living_zero_core import *
from living_zero_projection import (
    OnlineProjectionMemory,
    OwnershipProjector,
)
from async_projection_service import AsyncProjectionService
from async_dispatch_pipeline import AsyncWorkerPool

__all__ = [
    "OnlineProjectionMemory",
    "OwnershipProjector",
    "AsyncProjectionService",
    "AsyncWorkerPool",
]
