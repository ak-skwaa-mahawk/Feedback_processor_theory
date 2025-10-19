# backend/embeddings.py
# Enhanced with LRU cache + demo mode + Trinity integration
import os
import openai
import numpy as np
import hashlib
from functools import lru_cache
from typing import Optional
import io

openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")
USE_CACHE = os.getenv("USE_EMBEDDING_CACHE", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 10000))

# Cache statistics
cache_stats = {"hits": 0, "misses": 0, "total": 0}

def _hash_text(text: str) -> str:
    """Generate hash for cache key"""
    return hashlib.md5(text.encode()).hexdigest()

def _generate_demo_embedding(text: str, size: int = 512) -> np.ndarray:
    """Generate deterministic demo embedding (no API cost)"""
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16) % (2**32)
    rng = np.random.RandomState(seed)
    vec = rng.randn(size).astype(np.float32)
    vec /= (np.linalg.norm(vec) + 1e-12)
    return vec

@lru_cache(maxsize=CACHE_MAX_SIZE if USE_CACHE else 0)
def _text_to_embedding_cached(text_hash: str, text: str) -> tuple:
    """Cached embedding - returns tuple for hashability"""
    cache_stats["misses"] += 1
    
    if DEMO_MODE:
        vec = _generate_demo_embedding(text)
        return tuple(vec.tolist())
    
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    try:
        resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
        vec = np.array(resp["data"][0]["embedding"], dtype=np.float32)
        vec /= (np.linalg.norm(vec) + 1e-12)
        return tuple(vec.tolist())
    except Exception as e:
        print(f"OpenAI embedding error: {e}, using demo mode")
        vec = _generate_demo_embedding(text)
        return tuple(vec.tolist())

def text_to_embedding_openai(text: str) -> np.ndarray:
    """
    Get text embedding with caching
    Public API for embeddings
    """
    cache_stats["total"] += 1
    text = text.strip()
    
    if not text:
        return np.zeros(512, dtype=np.float32)
    
    if USE_CACHE:
        text_hash = _hash_text(text)
        embedding_tuple = _text_to_embedding_cached(text_hash, text)
        
        # Check if cache hit
        cache_info = _text_to_embedding_cached.cache_info()
        current_hits = cache_info.hits
        if current_hits > cache_stats["hits"]:
            cache_stats["hits"] = current_hits
    else:
        # No cache
        if DEMO_MODE:
            embedding_tuple = tuple(_generate_demo_embedding(text).tolist())
        else:
            resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
            vec = np.array(resp["data"][0]["embedding"], dtype=np.float32)
            vec /= (np.linalg.norm(vec) + 1e-12)
            embedding_tuple = tuple(vec.tolist())
    
    return np.array(embedding_tuple, dtype=np.float32)

def audio_bytes_to_embedding_openai(audio_bytes: bytes) -> np.ndarray:
    """
    Transcribe audio + generate embedding
    Pipeline: audio → Whisper → text → embedding
    """
    if DEMO_MODE:
        return _generate_demo_embedding("demo_audio", size=512)
    
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        try:
            # Try modern OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            text = transcription.text
        except (ImportError, AttributeError):
            # Fallback to legacy client
            transcription = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcription.get("text", "")
        
        if text:
            return text_to_embedding_openai(text)
        else:
            return np.zeros(512, dtype=np.float32)
    
    except Exception as e:
        print(f"Audio transcription error: {e}, using demo mode")
        return _generate_demo_embedding("error_audio", size=512)

def get_cache_stats() -> dict:
    """Get cache performance statistics"""
    total = cache_stats["total"]
    hits = cache_stats["hits"]
    misses = cache_stats["misses"]
    hit_rate = (hits / total * 100) if total > 0 else 0.0
    
    cache_info = _text_to_embedding_cached.cache_info() if USE_CACHE else None
    
    return {
        "enabled": USE_CACHE,
        "demo_mode": DEMO_MODE,
        "total_calls": total,
        "cache_hits": hits,
        "cache_misses": misses,
        "hit_rate_percent": hit_rate,
        "max_cache_size": CACHE_MAX_SIZE,
        "lru_info": {
            "hits": cache_info.hits if cache_info else 0,
            "misses": cache_info.misses if cache_info else 0,
            "currsize": cache_info.currsize if cache_info else 0
        }
    }

def clear_cache():
    """Clear embedding cache"""
    if USE_CACHE:
        _text_to_embedding_cached.cache_clear()
        cache_stats["hits"] = 0
        cache_stats["misses"] = 0
        cache_stats["total"] = 0
        print("Embedding cache cleared")