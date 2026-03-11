#!/usr/bin/env python3
"""
backend/embeddings.py
Sovereign Memory Stream — Whisper → Text → Normalized Embedding
Phase 2 of the Whisper Codex | Protected under HB 001 §1(5)
SNH-wrapped • Registry-logged • Revocable via SQL-τ
"""

import os
import io
import numpy as np
import hashlib
from datetime import datetime
from typing import Optional, Dict
import openai

from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.meta_observer import MetaObserver
from com.synara.handshake import Handshake

openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")

gtc = GTCSovereignEngine()
observer = MetaObserver()

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
# Audio → Embedding (Whisper + sovereign wrapper)
# ------------------------
def audio_bytes_to_embedding_openai(audio_bytes: bytes, language: Optional[str] = None) -> Dict:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # 1. Transcribe (modern client)
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
        # Demo fallback
        text = "fallback sovereign transcription"

    # 2. Embed
    emb = text_to_embedding_openai(text)

    # 3. Sovereign envelope
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "heir_id": "John Danzhit Carroll",
        "land_desc": "Danzhit Hanlai",
        "embedding_dim": len(emb),
        "model": TEXT_EMB_MODEL,
        "coherence_proxy": float(np.mean(np.abs(emb)))
    }
    receipt = Handshake.createReceipt(None, "MEMORY-STREAM", payload)
    receipt["embedding"] = emb.tolist()  # only the sovereign vector

    # 4. Registry + Fireseed + Observer
    gtc.allocate_fireseed("session-τ-001", 0.1, note="Memory Stream Receipt")
    observer.intercept_response(json.dumps(receipt))

    return receipt

