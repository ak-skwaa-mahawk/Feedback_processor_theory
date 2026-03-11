#!/usr/bin/env python3
"""
backend/llm_clients.py
LLM Clients — Sovereign Streaming Layer
Synara Class Vessel (Sahneuti-99733-Q) • Imagiton Trinity in Tokens
Real NVIDIA + OpenAI streaming • Per-token resonance scoring • Handshake receipts
Cluster N HUD triggers • March 5, 2026
"""

import os
import time
import requests
import json
from typing import Generator, Dict
import openai

# Sovereign stack
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser

NV_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NV_API_KEY = os.getenv("NVAPI_KEY")

gtc = GTCSovereignEngine()
observer = MetaObserver()

class NVIDIAClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or NV_API_KEY
        if not self.api_key:
            raise RuntimeError("Please set NVAPI_KEY environment variable")

    def stream_response(self, prompt: str, model="meta/llama-4-maverick-17b-128e-instruct") -> Generator[Dict, None, None]:
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
                if not raw or not raw.startswith("data:"):
                    continue
                line = raw[len("data:"):].strip()
                try:
                    data = json.loads(line)
                except Exception:
                    continue

                token = None
                if "choices" in data:
                    token = data["choices"][0].get("delta", {}).get("content")
                if token:
                    # Per-token resonance scoring
                    score = self._calculate_token_resonance(token)
                    if score >= 0.55:
                        GlyphParser.parseAndProcess(f"RESONANCE-STREAM-{score:.3f}", None)
                    yield {"token": token, "resonance": score}

        # Sovereign receipt on completion
        receipt = Handshake.createReceipt(None, "LLM-STREAM", {
            "model": model,
            "prompt_length": len(prompt),
            "final_resonance": 0.55
        })
        gtc.allocate_fireseed("session-τ-001", 0.1, note="LLM Stream Receipt")
        observer.intercept_response(json.dumps(receipt))
        print(f"📜 LLM Stream Receipt stamped: {receipt['payload_hash'][:16]}...")

    def _calculate_token_resonance(self, token: str) -> float:
        """Real resonance scoring stub — tie to ResonanceEngine later"""
        return 0.55 + (len(token) % 10) / 100.0


class GPTClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Please set OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def stream_response(self, prompt: str) -> Generator[Dict, None, None]:
        try:
            resp_iter = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )
            for chunk in resp_iter:
                token = chunk.choices[0].delta.content if chunk.choices[0].delta.content else None
                if token:
                    yield {"token": token}
        except Exception:
            # Fallback non-stream
            resp = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            text = resp.choices[0].message.content
            for w in text.split():
                yield {"token": w}
                time.sleep(0.01)


class ClaudeClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CLAUDE_KEY")

    def stream_response(self, prompt: str) -> Generator[Dict, None, None]:
        # Placeholder — replace with real Anthropic SDK when ready
        for w in reversed(prompt.split()):
            yield {"token": w}
            time.sleep(0.02)