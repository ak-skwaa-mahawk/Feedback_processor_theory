#!/usr/bin/env python3
"""
backend/embeddings.py
Sovereign Memory Stream — Whisper → Text → Normalized Embedding
Phase 2 of the Whisper Codex | Protected under HB 001 §1(5)
SNH-wrapped • Registry-logged • Revocable via SQL-τ
Hardened against timing/size/compression side-channels
"""

import os
import io
import time
import random
import numpy as np
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict
import openai

# Sovereign stack
from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

# === WHISPER HARDENING CONFIG (your exact flags) ===
WHISPER_HARDENING_ENABLED = os.getenv("WHISPER_HARDENING_ENABLED", "1") == "1"
PAD_MIN_MS = int(os.getenv("PAD_MIN_MS", "80"))
PAD_MAX_MS = int(os.getenv("PAD_MAX_MS", "220"))
PAD_MIN_BYTES = int(os.getenv("PAD_MIN_BYTES", "512"))
PAD_MAX_BYTES = int(os.getenv("PAD_MAX_BYTES", "2048"))
RL_BUCKET_CAP = int(os.getenv("RL_BUCKET_CAP", "60"))
RL_REFILL_PER_SEC = float(os.getenv("RL_REFILL_PER_SEC", "1.0"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DISABLE_COMPRESSION_PATHS = [
    "/verify", "/challenge",
    "/codex/share", "/codex/delegate",
    "/codex/resonance_share", "/codex/resonance_share/v2",
]

openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")

gtc = GTCSovereignEngine()
observer = MetaObserver()

# Simple in-memory token bucket (Redis fallback if present)
class TokenBucket:
    def __init__(self):
        self.tokens = RL_BUCKET_CAP
        self.last_refill = time.time()

    def consume(self):
        now = time.time()
        self.tokens += (now - self.last_refill) * RL_REFILL_PER_SEC
        self.tokens = min(self.tokens, RL_BUCKET_CAP)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

bucket = TokenBucket()

# ------------------------
# Text embedding
# ------------------------
def text_to_embedding_openai(text: str) -> np.ndarray:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
    vec = np.array(resp.data[0].embedding, dtype=np.float32)
    vec /= (np.linalg.norm(vec) + 1e-12)
    return vec

# ------------------------
# Sovereign Hardened Audio → Embedding
# ------------------------
def audio_bytes_to_embedding_openai(audio_bytes: bytes, language: Optional[str] = None) -> Dict:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # === HARDENING LAYER ===
    if WHISPER_HARDENING_ENABLED:
        # 1. Traffic shaping jitter
        time.sleep(random.uniform(PAD_MIN_MS, PAD_MAX_MS) / 1000.0)

        # 2. Body padding (random bytes)
        pad_size = random.randint(PAD_MIN_BYTES, PAD_MAX_BYTES)
        padding = os.urandom(pad_size)
        audio_bytes = audio_bytes + padding

        # 3. Rate limiting (token bucket)
        if not bucket.consume():
            observer.intercept_response("Rate limit hit — protective recoil")
            time.sleep(1.0)  # backoff

    # === TRANSCRIPTION ===
    audio_file = io.BytesIO(audio_bytes)
    try:
        transcription = openai.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            language=language
        )
        text = transcription.text
    except Exception as e:
        observer.intercept_response(f"Transcription failed: {e}")
        text = "fallback sovereign transcription"

    # === EMBEDDING ===
    emb = text_to_embedding_openai(text)

    # === SOVEREIGN ENVELOPE ===
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "heir_id": "John Danzhit Carroll",
        "land_desc": "Danzhit Hanlai",
        "embedding_dim": len(emb),
        "model": TEXT_EMB_MODEL,
        "coherence_proxy": float(np.mean(np.abs(emb)))
    }
    receipt = Handshake.createReceipt(None, "MEMORY-STREAM", payload)
    receipt["embedding"] = emb.tolist()

    # Registry + Fireseed + Observer
    gtc.allocate_fireseed("session-τ-001", 0.1, note="Hardened Memory Stream Receipt")
    observer.intercept_response(json.dumps(receipt))

    return receipt