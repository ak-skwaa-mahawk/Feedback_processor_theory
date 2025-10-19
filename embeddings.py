# backend/embeddings.py
# Text & audio embedding helpers.
# Text embeddings use sentence-transformers by default (fast and local).
# Audio embedding: placeholder — recommended to replace with Whisper2 / openai audio embedding or ONNX model.

import os
import numpy as np
from typing import Optional

# Text embedding: SentenceTransformers (fast local models)
try:
    from sentence_transformers import SentenceTransformer
    _TEXT_ENCODER = SentenceTransformer(os.getenv("TEXT_EMB_MODEL", "all-MiniLM-L6-v2"))
except Exception as e:
    _TEXT_ENCODER = None
    print("Warning: sentence_transformers not available:", e)

def text_to_embedding(text: str) -> np.ndarray:
    """
    Returns a normalized embedding vector for text.
    """
    if _TEXT_ENCODER is None:
        # fallback: random vector (for demo only)
        vec = np.random.rand(384).astype(np.float32)
    else:
        vec = _TEXT_ENCODER.encode(text, convert_to_numpy=True)
    # normalize
    norm = np.linalg.norm(vec) + 1e-12
    return vec.astype(np.float32) / norm

# Audio embedding stub:
def audio_bytes_to_embedding(raw_audio_bytes: bytes) -> np.ndarray:
    """
    Convert raw audio bytes (float32 PCM) into an embedding vector.
    Replace with Whisper / wav2vec2 / OpenAI audio embeddings for production.
    """
    # placeholder: random vector (demo)
    vec = np.random.rand(384).astype(np.float32)
    norm = np.linalg.norm(vec) + 1e-12
    return vec / norm