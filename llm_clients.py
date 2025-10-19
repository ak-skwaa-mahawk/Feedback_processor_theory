"""
LLM Clients - Streaming interfaces for OpenAI, NVIDIA, and Anthropic
"""

import os
import time
import requests
import json
import logging
from typing import AsyncIterator, Iterator

logger = logging.getLogger(__name__)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NVAPI_KEY = os.getenv("NVAPI_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ==================
# NVIDIA NIM Client
# ==================

class NVIDIAClient:
    """NVIDIA NIM API client with SSE streaming"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or NVAPI_KEY
        self.model = model or os.getenv("NV_MODEL", "meta/llama-3.1-405b-instruct")
        self.endpoint = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        if not self.api_key:
            raise RuntimeError("NVAPI_KEY not set")
        
        logger.info(f"NVIDIA client initialized with model: {self.model}")
    
    def stream_response(self, prompt: str) -> Iterator[dict]:
        """
        Stream tokens from NVIDIA NIM API
        Yields: {"token": str}
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7,
            "stream": True
        }
        
        try:
            with requests.post(
                self.endpoint, 
                headers=headers, 
                json=payload, 
                stream=True, 
                timeout=300
            ) as resp:
                resp.raise_for_status()
                
                for raw_line in resp.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    
                    line = raw_line.strip()
                    
                    # Parse SSE format
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    
                    if line == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    # Extract token from various possible structures
                    token = None
                    
                    if "choices" in chunk:
                        try:
                            delta = chunk["choices"][0].get("delta", {})
                            token = delta.get("content")
                        except (IndexError, KeyError):
                            pass
                    
                    if not token:
                        token = chunk.get("content") or chunk.get("text")
                    
                    if token:
                        yield {"token": token}
                        time.sleep(0.001)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"NVIDIA API error: {e}")
            raise


# ==================
# OpenAI GPT Client
# ==================

class GPTClient:
    """OpenAI GPT client with real streaming"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        
        # Import OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.use_modern_client = True
        except ImportError:
            # Fallback for older openai package
            import openai
            openai.api_key = self.api_key
            self.client = openai
            self.use_modern_client = False
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def stream_response(self, prompt: str) -> Iterator[dict]:
        """
        Stream tokens from OpenAI Chat API
        Yields: {"token": str}
        """
        try:
            if self.use_modern_client:
                # Modern OpenAI client (v1.0+)
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield {"token": chunk.choices[0].delta.content}
            
            else:
                # Legacy OpenAI client
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in response:
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield {"token": token}
        
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            # Fallback: non-streaming response
            try:
                if self.use_modern_client:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    text = response.choices[0].message.content
                else:
                    response = self.client.ChatCompletion.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    text = response["choices"][0]["message"]["content"]
                
                # Simulate streaming by yielding words
                for word in text.split():
                    yield {"token": word + " "}
                    time.sleep(0.01)
            
            except Exception as fallback_error:
                logger.error(f"OpenAI fallback error: {fallback_error}")
                raise


# ==================
# Anthropic Claude Client
# ==================

class ClaudeClient:
    """Anthropic Claude client with streaming"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
        
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        
        # Import Anthropic client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.available = True
        except ImportError:
            logger.warning("Anthropic package not installed. Install with: pip install anthropic")
            self.available = False
        
        logger.info(f"Claude client initialized with model: {self.model}")
    
    def stream_response(self, prompt: str) -> Iterator[dict]:
        """
        Stream tokens from Anthropic Claude API
        Yields: {"token": str}
        """
        if not self.available:
            # Fallback: simulate streaming for demo
            for word in prompt.split()[:10]:
                yield {"token": f"[Claude unavailable] {word} "}
                time.sleep(0.05)
            return
        
        try:
            # Anthropic streaming
            with self.client.messages.stream(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    if text:
                        yield {"token": text}
        
        except Exception as e:
            logger.error(f"Claude streaming error: {e}")
            
            # Fallback: non-streaming
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                text = message.content[0].text
                
                # Simulate streaming
                for word in text.split():
                    yield {"token": word + " "}
                    time.sleep(0.01)
            
            except Exception as fallback_error:
                logger.error(f"Claude fallback error: {fallback_error}")
                raise


# ==================
# Utility Functions
# ==================

def test_client(client_class, prompt="Hello, test streaming!"):
    """Test a client implementation"""
    try:
        client = client_class()
        print(f"\nTesting {client_class.__name__}...")
        print("-" * 50)
        
        tokens = []
        for chunk in client.stream_response(prompt):
            token = chunk.get("token", "")
            tokens.append(token)
            print(token, end="", flush=True)
        
        print("\n" + "-" * 50)
        print(f"✓ Received {len(tokens)} tokens")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    """Test all clients"""
    import sys
    
    print("=" * 50)
    print("LLM Client Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test GPT
    if OPENAI_API_KEY:
        results["GPT"] = test_client(GPTClient)
    else:
        print("\n⚠ Skipping GPT (no OPENAI_API_KEY)")
        results["GPT"] = False
    
    # Test NVIDIA
    if NVAPI_KEY:
        results["NVIDIA"] = test_client(NVIDIAClient)
    else:
        print("\n⚠ Skipping NVIDIA (no NVAPI_KEY)")
        results["NVIDIA"] = False
    
    # Test Claude
    if ANTHROPIC_API_KEY:
        results["Claude"] = test_client(ClaudeClient)
    else:
        print("\n⚠ Skipping Claude (no ANTHROPIC_API_KEY)")
        results["Claude"] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
    print("=" * 50)
    
    # Exit code
    sys.exit(0 if all(results.values()) else 1)
# backend/llm_clients.py
# LLM streaming clients. NVIDIA implemented (SSE). GPT/Claude have placeholders for streaming integration.
import os
import requests
import json
import time

NV_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NV_API_KEY = os.getenv("NVAPI_KEY")  # set in environment

class NVIDIAClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or NV_API_KEY
        if not self.api_key:
            raise RuntimeError("Please set NVAPI_KEY environment variable")

    def stream_response(self, prompt, model="meta/llama-4-maverick-17b-128e-instruct"):
        """
        Generator that yields token dicts as they arrive from NVIDIA SSE stream.
        Each yield: {"token": "<text piece>"}
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7,
            "stream": True
        }
        with requests.post(NV_ENDPOINT, headers=headers, json=payload, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            # resp.iter_lines yields lines (SSE style). Lines may be 'data: {...}' or raw json
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                line = raw.strip()
                # If SSE prefixed with "data: " remove it
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                # Some servers send 'event: ...' or keepalive; ignore non-json
                try:
                    payload = json.loads(line)
                except Exception:
                    # Not JSON — ignore or print for debug
                    continue
                # Depending on provider, structure may vary. Standardize:
                token_text = None
                # NVIDIA sometimes uses 'choices' structure — try common fields
                if "choices" in payload:
                    try:
                        token_text = payload["choices"][0].get("delta", {}).get("content")
                    except Exception:
                        token_text = None
                # fallback to message fields
                if not token_text:
                    token_text = payload.get("content") or payload.get("text") or payload.get("message")
                if token_text:
                    # yield token chunk (could be partial token or token-by-token depending on model)
                    yield {"token": token_text}
                # small sleep to avoid busy-loop if provider returns a lot
                time.sleep(0.001)


class GPTClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GPT_KEY")

    def stream_response(self, prompt):
        """
        Replace with real GPT streaming code (OpenAI streaming, etc.)
        This placeholder yields words with a small delay for demo.
        """
        for w in prompt.split():
            yield {"token": w}
            time.sleep(0.02)


class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CLAUDE_KEY")

    def stream_response(self, prompt):
        """Placeholder streaming for Claude — replace with real streaming implementation"""
        words = prompt.split()[::-1]
        for w in words:
            yield {"token": w}
            time.sleep(0.02)