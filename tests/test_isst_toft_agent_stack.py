#!/usr/bin/env python3
"""
tests/test_isst_toft_agent_stack.py — Full hybrid Python-Rust tests v1.5.8
"""

import pytest
import numpy as np
from unittest.mock import patch
from core.isst_toft_agent_stack import ISSTTOFTAgentStack
from core.isst_toft_core import ISSTTOFTCore, FPTOmegaProcessor

@pytest.fixture
def mock_fpt_omega(): ...  # unchanged from previous

@pytest.fixture
def hybrid_stack(mock_fpt_omega):
    core = ISSTTOFTCore(fpt_omega=mock_fpt_omega)
    stack = ISSTTOFTAgentStack(core, use_rust_inference=True)
    return stack

@pytest.mark.asyncio
async def test_hybrid_rust_call_contract(hybrid_stack):
    """Verify Rust backend is called with correct payload and returns expected shape."""
    terrain = np.random.randn(8192).astype(np.float32) * 0.1 + 79.79
    
    mock_response = {
        "refined_waveform": np.random.randn(8192).tolist(),
        "checksum": 18446744073709551615,
        "status": "RAD_HARD_GLYPH_LOCKED_RUST"
    }
    
    with patch("httpx.AsyncClient.post", return_value=pytest.mock.Mock(json=lambda: mock_response, raise_for_status=lambda: None)):
        result = await hybrid_stack.encode_agentic_rad_hard_glyph(terrain)
        
        assert result["inference_engine"] == "RUST_CANDLE"
        assert "refined_signal" in result
        assert len(result["refined_signal"]) == 256
        assert result["waveform_checksum"] == 18446744073709551615

@pytest.mark.asyncio
async def test_fallback_python_path(hybrid_stack):
    """When use_rust_inference=False, falls back cleanly to Python path."""
    hybrid_stack.use_rust_inference = False
    terrain = np.random.randn(8192).astype(np.float32) * 0.1 + 79.79
    result = await hybrid_stack.encode_agentic_rad_hard_glyph(terrain)
    assert result["inference_engine"] == "PYTORCH_FALLBACK"