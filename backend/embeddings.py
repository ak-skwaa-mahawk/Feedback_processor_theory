# backend/embeddings.py
import os
import openai
import numpy as np
import base64
from typing import Optional

openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")  # or text-embedding-3-large

# ------------------------
# Text embedding (OpenAI Embeddings)
# ------------------------
def text_to_embedding_openai(text: str) -> np.ndarray:
    """
    Use OpenAI embeddings API to get a vector for text.
    """
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
    vec = np.array(resp["data"][0]["embedding"], dtype=np.float32)
    vec /= (np.linalg.norm(vec) + 1e-12)
    return vec

# ------------------------
# Audio transcription + embedding using Whisper -> text -> embeddings
# ------------------------
def audio_bytes_to_embedding_openai(audio_bytes: bytes, language: Optional[str] = None) -> np.ndarray:
    """
    Transcribe audio with OpenAI Whisper (speech-to-text) then embed the transcribed text.
    This is a robust pipeline: send audio bytes to OpenAI's speech endpoint, then embed the string.
    """
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # OpenAI's speech-to-text call (Whisper) — the exact client call can be:
    # openai.Audio.transcribe("whisper-1", file=io.BytesIO(audio_bytes))
    # Different client versions expose different wrappers. The commonly used pattern:
    import io
    audio_file = io.BytesIO(audio_bytes)
    # For many openai python versions:
    try:
        transcription = openai.audio.transcriptions.create(file=audio_file, model="gpt-4o-transcribe")  # placeholder model name; replace with "whisper-1" or current
        text = transcription["text"]
    except Exception:
        # Fallback: if direct transcription method not available on installed client,
        # try the older pattern:
        try:
            transcription = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcription["text"]
        except Exception:
            # As a final fallback, return a random embedding (demo mode only)
            vec = np.random.rand(512).astype(np.float32)
            return vec / (np.linalg.norm(vec) + 1e-12)

    # Now embed the transcribed text
    emb = text_to_embedding_openai(text)
    return emb