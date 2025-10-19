"""
Embeddings Module - Audio transcription and text embedding with caching
"""

import os
import openai
import numpy as np
import hashlib
from functools import lru_cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
TEXT_EMB_MODEL = os.getenv("TEXT_EMB_MODEL", "text-embedding-3-small")
USE_CACHE = os.getenv("USE_EMBEDDING_CACHE", "true").lower() == "true"
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 10000))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Cache statistics
cache_stats = {"hits": 0, "misses": 0, "total_calls": 0}


def _hash_text(text: str) -> str:
    """Generate hash for cache key"""
    return hashlib.md5(text.encode()).hexdigest()


def _generate_demo_embedding(text: str, size: int = 512) -> np.ndarray:
    """Generate deterministic demo embedding (no API call)"""
    # Use hash as seed for reproducibility
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16) % (2**32)
    rng = np.random.RandomState(seed)
    vec = rng.randn(size).astype(np.float32)
    vec /= (np.linalg.norm(vec) + 1e-12)
    return vec


@lru_cache(maxsize=CACHE_MAX_SIZE if USE_CACHE else 0)
def _text_to_embedding_cached(text_hash: str, text: str) -> tuple:
    """
    Cached embedding function
    Returns tuple for hashability (required by lru_cache)
    """
    cache_stats["misses"] += 1
    
    if DEMO_MODE:
        logger.debug(f"Demo embedding for: {text[:50]}...")
        vec = _generate_demo_embedding(text)
        return tuple(vec.tolist())
    
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    try:
        resp = openai.embeddings.create(
            model=TEXT_EMB_MODEL,
            input=text
        )
        vec = np.array(resp.data[0].embedding, dtype=np.float32)
        vec /= (np.linalg.norm(vec) + 1e-12)
        
        logger.debug(f"OpenAI embedding generated for: {text[:50]}...")
        return tuple(vec.tolist())
        
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        # Fallback to demo embedding
        vec = _generate_demo_embedding(text)
        return tuple(vec.tolist())


def text_to_embedding_openai(text: str) -> np.ndarray:
    """
    Get text embedding with caching
    Main public interface for text embeddings
    """
    cache_stats["total_calls"] += 1
    
    # Strip whitespace
    text = text.strip()
    if not text:
        return np.zeros(512, dtype=np.float32)
    
    # Check cache
    if USE_CACHE:
        text_hash = _hash_text(text)
        embedding_tuple = _text_to_embedding_cached(text_hash, text)
        
        # Check if it was a cache hit
        cache_info = _text_to_embedding_cached.cache_info()
        if cache_info.hits > cache_stats["hits"]:
            cache_stats["hits"] += 1
            logger.debug(f"Cache HIT for: {text[:50]}...")
    else:
        # No cache - direct call
        if DEMO_MODE:
            embedding_tuple = tuple(_generate_demo_embedding(text).tolist())
        else:
            resp = openai.embeddings.create(model=TEXT_EMB_MODEL, input=text)
            vec = np.array(resp.data[0].embedding, dtype=np.float32)
            vec /= (np.linalg.norm(vec) + 1e-12)
            embedding_tuple = tuple(vec.tolist())
    
    # Convert back to numpy array
    return np.array(embedding_tuple, dtype=np.float32)


def audio_bytes_to_embedding_openai(audio_bytes: bytes, 
                                    language: Optional[str] = None) -> np.ndarray:
    """
    Transcribe audio with Whisper and generate text embedding
    Pipeline: audio → Whisper transcription → text embedding
    """
    if DEMO_MODE:
        logger.debug("Demo mode: generating random audio embedding")
        return _generate_demo_embedding("demo_audio", size=512)
    
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    try:
        # Transcribe audio using Whisper
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"  # OpenAI requires a filename
        
        # Attempt transcription
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
            text = transcription.text
            logger.info(f"Transcribed audio: {text[:100]}...")
            
        except AttributeError:
            # Fallback for older openai package versions
            transcription = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language=language
            )
            text = transcription["text"]
            logger.info(f"Transcribed audio (legacy): {text[:100]}...")
        
        # Generate embedding from transcribed text
        if text:
            embedding = text_to_embedding_openai(text)
            return embedding
        else:
            logger.warning("Empty transcription - returning zero embedding")
            return np.zeros(512, dtype=np.float32)
    
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        # Return demo embedding as fallback
        return _generate_demo_embedding("error_audio", size=512)


def get_cache_stats() -> dict:
    """Get cache performance statistics"""
    total = cache_stats["total_calls"]
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
        "lru_cache_info": {
            "hits": cache_info.hits if cache_info else