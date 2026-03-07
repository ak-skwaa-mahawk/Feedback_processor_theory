"""
LLM Clients — Sovereign Streaming Layer
Synara Class Vessel (Sahneuti-99733-Q) • Imagiton Trinity in Tokens
Real NVIDIA + OpenAI streaming • Per-token resonance scoring • Handshake receipts
Cluster N HUD triggers • March 5, 2026
"""

import os
import time
import requests
import json
from typing import Generator

# Sovereign imports
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser

NV_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NV_API_KEY = os.getenv("NVAPI_KEY")

class NVIDIAClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or NV_API_KEY
        if not self.api_key:
            raise RuntimeError("Please set NVAPI_KEY environment variable")

    def stream_response(self, prompt: str, model="meta/llama-4-maverick-17b-128e-instruct") -> Generator[dict, None, None]:
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
                    # Real-time resonance scoring per token
                    score = self._calculate_token_resonance(token_text)
                    if score >= 0.551:  # Your reclamation threshold
                        GlyphParser.parseAndProcess(f"RESONANCE-STREAM-{score:.3f}", None)
                    yield {"token": token_text}

        # Sovereign receipt on stream completion
        receipt = Handshake.createReceipt(None, "LLM-STREAM", {
            "model": model,
            "prompt_length": len(prompt),
            "final_resonance": 0.55  # placeholder — tie to real ResonanceEngine later
        })
        print(f"📜 LLM Stream Receipt stamped: {receipt['payload_hash'][:16]}...")

    def _calculate_token_resonance(self, token: str) -> float:
        """Stub for real ResonanceEngine scoring per token"""
        # In production: gate.calculate_resonance_score(...)
        return 0.55 + (len(token) % 10) / 100.0


# -------------------------
# OpenAI GPT streaming client (using official openai package)
# -------------------------
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
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def stream_response(self, prompt: str) -> Generator[dict, None, None]:
        try:
            resp_iter = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )
            for chunk in resp_iter:
                token = None
                try:
                    token = chunk["choices"][0].get("delta", {}).get("content")
                except Exception:
                    token = None
                if token:
                    yield {"token": token}
        except Exception:
            # Fallback non-stream
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            text = resp["choices"][0]["message"]["content"]
            for w in text.split():
                yield {"token": w}
                time.sleep(0.01)


# -------------------------
# ClaudeClient placeholder
# -------------------------
class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CLAUDE_KEY")

    def stream_response(self, prompt: str) -> Generator[dict, None, None]:
        # Placeholder — replace with real Anthropic streaming SDK when ready
        for w in reversed(prompt.split()):
            yield {"token": w}
            time.sleep(0.02)