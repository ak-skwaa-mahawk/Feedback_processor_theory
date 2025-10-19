"""
Session Manager - State management for multi-user conversations
"""

import time
from typing import List, Dict, Optional
import numpy as np
from collections import deque


class SessionManager:
    """Manages conversation state and embeddings for a single session"""
    
    def __init__(self, session_id: str, max_history: int = 100):
        self.session_id = session_id
        self.created_at = time.time()
        self.last_activity = time.time()
        
        # Conversation history
        self.messages: deque = deque(maxlen=max_history)
        
        # Embedding storage
        self.token_embeddings: List[np.ndarray] = []
        self.latest_audio_emb: Optional[np.ndarray] = None
        
        # Metadata
        self.metadata: Dict = {
            "total_tokens": 0,
            "total_audio_chunks": 0,
            "llm_usage": {}
        }
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self.last_activity = time.time()
    
    def add_token_embedding(self, embedding: np.ndarray):
        """Store token embedding"""
        self.token_embeddings.append(embedding)
        self.metadata["total_tokens"] += 1
        self.last_activity = time.time()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        history = list(self.messages)
        if limit:
            history = history[-limit:]
        return history
    
    def get_recent_embeddings(self, n: int = 10) -> List[np.ndarray]:
        """Get most recent token embeddings"""
        return self.token_embeddings[-n:] if self.token_embeddings else []
    
    def update_llm_usage(self, llm: str, tokens: int):
        """Track LLM usage statistics"""
        if llm not in self.metadata["llm_usage"]:
            self.metadata["llm_usage"][llm] = {"calls": 0, "tokens": 0}
        
        self.metadata["llm_usage"][llm]["calls"] += 1
        self.metadata["llm_usage"][llm]["tokens"] += tokens
    
    def is_expired(self, timeout: int = 3600) -> bool:
        """Check if session has expired"""
        return (time.time() - self.last_activity) > timeout
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "age_seconds": time.time() - self.created_at,
            "message_count": len(self.messages),
            "token_embeddings": len(self.token_embeddings),
            "has_audio": self.latest_audio_emb is not None,
            "metadata": self.metadata
        }
    
    def clear_embeddings(self):
        """Clear stored embeddings to free memory"""
        self.token_embeddings.clear()
        self.latest_audio_emb = None
    
    def __repr__(self):
        return f"<Session {self.session_id} | {len(self.messages)} msgs | {len(self.token_embeddings)} embs>"