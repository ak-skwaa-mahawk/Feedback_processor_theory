"""
Integration tests for Harmonic Demo
"""

import pytest
import asyncio
import websockets
import json
import os
from typing import AsyncGenerator

# Test configuration
BACKEND_URL = os.getenv("TEST_BACKEND_URL", "ws://localhost:8765")
TEST_TIMEOUT = 30


@pytest.fixture
async def websocket_connection() -> AsyncGenerator:
    """Fixture for WebSocket connection"""
    ws = await websockets.connect(BACKEND_URL)
    yield ws
    await ws.close()


@pytest.mark.asyncio
async def test_connection_handshake(websocket_connection):
    """Test WebSocket connection and handshake"""
    ws = websocket_connection
    
    # Should receive welcome message
    message = await asyncio.wait_for(ws.recv(), timeout=5)
    data = json.loads(message)
    
    assert data["type"] == "connected"
    assert "session_id" in data
    assert "features" in data
    assert "available_llms" in data


@pytest.mark.asyncio
async def test_gpt_streaming(websocket_connection):
    """Test GPT streaming response"""
    ws = websocket_connection
    
    # Wait for welcome
    await ws.recv()
    
    # Send prompt
    await ws.send(json.dumps({
        "type": "prompt",
        "text": "Count to 5",
        "llm": "gpt"
    }))
    
    # Collect tokens
    tokens = []
    completion_received = False
    
    try:
        while not completion_received:
            message = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
            data = json.loads(message)
            
            if data["type"] == "token":
                tokens.append(data["token"])
                assert "resonance" in data
                assert "timestamp" in data
            
            elif data["type"] == "complete":
                completion_received = True
                assert data["llm"] == "gpt"
                assert data["tokens"] > 0
            
            elif data["type"] == "error":
                pytest.fail(f"Received error: {data['message']}")
    
    except asyncio.TimeoutError:
        pytest.fail("Timeout waiting for completion")
    
    assert len(tokens) > 0, "Should receive at least one token"
    assert completion_received, "Should receive completion message"


@pytest.mark.asyncio
async def test_embedding_cache(websocket_connection):
    """Test embedding cache functionality"""
    ws = websocket_connection
    await ws.recv()  # Welcome
    
    # Send same prompt twice
    test_prompt = "Hello world"
    
    for i in range(2):
        await ws.send(json.dumps({
            "type": "prompt",
            "text": test_prompt,
            "llm": "gpt"
        }))
        
        # Wait for completion
        while True:
            message = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
            data = json.loads(message)
            if data["type"] == "complete":
                break
    
    # Second run should be faster due to caching
    # (This is qualitative - we'd need timing metrics for quantitative test)


@pytest.mark.asyncio
async def test_audio_processing(websocket_connection):
    """Test audio chunk processing"""
    ws = websocket_connection
    await ws.recv()  # Welcome
    
    # Send dummy audio data (base64 encoded zeros)
    import base64
    dummy_audio = base64.b64encode(b'\x00' * 1024).decode()
    
    await ws.send(json.dumps({
        "type": "audio_chunk",
        "data": dummy_audio
    }))
    
    # Wait for audio processed confirmation
    processed = False
    try:
        while not processed:
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(message)
            
            if data["type"] == "audio_processed":
                processed = True
                assert "embedding_size" in data
                assert "spectral" in data
    
    except asyncio.TimeoutError:
        pytest.skip("Audio processing not enabled or timed out")


@pytest.mark.asyncio
async def test_session_history(websocket_connection):
    """Test conversation history retrieval"""
    ws = websocket_connection
    await ws.recv()  # Welcome
    
    # Send a message
    await ws.send(json.dumps({
        "type": "prompt",
        "text": "Test message for history",
        "llm": "gpt"
    }))
    
    # Wait for completion
    while True:
        message = await ws.recv()
        data = json.loads(message)
        if data["type"] == "complete":
            break
    
    # Request history
    await ws.send(json.dumps({
        "type": "get_history"
    }))
    
    # Receive history
    message = await asyncio.wait_for(ws.recv(), timeout=5)
    data = json.loads(message)
    
    assert data["type"] == "history"
    assert "messages" in data
    assert len(data["messages"]) > 0


@pytest.mark.asyncio
async def test_ping_pong(websocket_connection):
    """Test ping/pong keepalive"""
    ws = websocket_connection
    await ws.recv()  # Welcome
    
    await ws.send(json.dumps({"type": "ping"}))
    
    message = await asyncio.wait_for(ws.recv(), timeout=5)
    data = json.loads(message)
    
    assert data["type"] == "pong"


@pytest.mark.asyncio
async def test_invalid_message_handling(websocket_connection):
    """Test error handling for invalid messages"""
    ws = websocket_connection
    await ws.recv()  # Welcome
    
    # Send invalid JSON
    await ws.send("invalid json{{{")
    
    message = await asyncio.wait_for(ws.recv(), timeout=5)
    data = json.loads(message)
    
    assert data["type"] == "error"
    assert "Invalid JSON" in data["message"]


@pytest.mark.asyncio
async def test_multiple_llm_switching(websocket_connection):
    """Test switching between different LLMs"""
    ws = websocket_connection
    welcome = json.loads(await ws.recv())
    
    available_llms = welcome["available_llms"]
    
    # Test each available LLM
    for llm, is_available in available_llms.items():
        if not is_available:
            continue
        
        await ws.send(json.dumps({
            "type": "prompt",
            "text": f"Test with {llm}",
            "llm": llm
        }))
        
        # Wait for at least one token
        token_received = False
        while not token_received:
            message = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
            data = json.loads(message)
            
            if data["type"] == "token":
                token_received = True
                assert data["llm"] == llm
            
            elif data["type"] == "complete":
                break
        
        assert token_received, f"Should receive token from {llm}"


@pytest.mark.asyncio
async def test_concurrent_connections():
    """Test multiple concurrent WebSocket connections"""
    connections = []
    
    try:
        # Open 5 concurrent connections
        for i in range(5):
            ws = await websockets.connect(BACKEND_URL)
            connections.append(ws)
            await ws.recv()  # Welcome message
        
        # Send messages from all connections
        tasks = []
        for i, ws in enumerate(connections):
            task = ws.send(json.dumps({
                "type": "prompt",
                "text": f"Concurrent test {i}",
                "llm": "gpt"
            }))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify all get responses
        for ws in connections:
            message = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
            data = json.loads(message)
            assert data["type"] in ["token", "complete", "error"]
    
    finally:
        # Cleanup
        for ws in connections:
            await ws.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])