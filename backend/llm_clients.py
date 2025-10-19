# backend/llm_clients.py
import os
import time
import requests
import json

# NVIDIA client (unchanged)
NV_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NV_API_KEY = os.getenv("NVAPI_KEY")

class NVIDIAClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or NV_API_KEY
        if not self.api_key:
            raise RuntimeError("Please set NVAPI_KEY environment variable")

    def stream_response(self, prompt, model="meta/llama-4-maverick-17b-128e-instruct"):
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
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                line = raw.strip()
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                token_text = None
                if "choices" in payload:
                    try:
                        token_text = payload["choices"][0].get("delta", {}).get("content")
                    except Exception:
                        token_text = None
                if not token_text:
                    token_text = payload.get("content") or payload.get("text") or payload.get("message")
                if token_text:
                    yield {"token": token_text}
                time.sleep(0.001)


# -------------------------
# OpenAI GPT streaming client
# -------------------------
# This uses the official 'openai' Python package (install via pip).
# It calls ChatCompletions with stream=True and yields tokens as they arrive.

try:
    import openai
except Exception:
    openai = None

class GPTClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Please set OPENAI_API_KEY environment variable")
        if openai is None:
            raise RuntimeError("openai package not installed. pip install openai")
        openai.api_key = self.api_key
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")  # change model as desired

    def stream_response(self, prompt):
        """
        Synchronous generator that yields token pieces from OpenAI chat streaming.
        Uses client.chat.completions.create(..., stream=True) or the modern OpenAI client.
        """
        # Many OpenAI clients return an iterable when stream=True. The exact structure
        # depends on the client version. We handle the common pattern of 'choices' chunks.
        try:
            # classic pattern with openai python library
            resp_iter = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role":"user","content": prompt}],
                temperature=0.7,
                stream=True
            )
            # resp_iter is an iterator that yields dict-like chunks
            for chunk in resp_iter:
                # chunk structure commonly: {"choices":[{"delta":{"content":"..."},"index":0,"finish_reason":None}], ...}
                token = None
                try:
                    token = chunk["choices"][0].get("delta", {}).get("content")
                except Exception:
                    token = None
                if token:
                    yield {"token": token}
        except TypeError:
            # Fallback for other client interfaces: try iterating .get("choices") or print chunk
            # If streaming isn't supported in installed client, fall back to full completion (non-stream)
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role":"user","content": prompt}],
                temperature=0.7
            )
            text = resp["choices"][0]["message"]["content"]
            # naive word yield to simulate streaming
            for w in text.split():
                yield {"token": w}
                time.sleep(0.01)


# -------------------------
# ClaudeClient placeholder (you can implement streaming with Anthropic SDK)
# -------------------------
class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CLAUDE_KEY")

    def stream_response(self, prompt):
        # Placeholder: yield words for demo; replace with Anthropic streaming SDK code
        for w in prompt.split():
            yield {"token": w}
            time.sleep(0.02)