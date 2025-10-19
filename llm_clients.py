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