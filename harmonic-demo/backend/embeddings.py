# backend/embeddings.py
import os
import openai
import numpy as np
import base64
import io

openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")

def text_to_embedding_openai(text: str) -> np.ndarray:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
    vec = np.array(resp["data"][0]["embedding"], dtype=np.float32)
    vec /= (np.linalg.norm(vec) + 1e-12)
    return vec

def audio_bytes_to_embedding_openai(audio_bytes: bytes) -> np.ndarray:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    audio_file = io.BytesIO(audio_bytes)
    try:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        text = transcription["text"]
    except Exception:
        try:
            transcription = openai.audio.transcriptions.create(file=audio_file, model="whisper-1")
            text = transcription.get("text", "")
        except Exception:
            vec = np.random.rand(512).astype(np.float32)
            return vec / (np.linalg.norm(vec) + 1e-12)
    emb = text_to_embedding_openai(text)
    return emb