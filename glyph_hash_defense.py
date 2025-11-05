# glyph_hash_defense.py
def entropy_bound(prompt: str) -> bool:
    """Reject high-entropy (obfuscated) prompts"""
    bytes_entropy = len(set(prompt.encode())) / len(prompt.encode())
    return bytes_entropy > 0.3  # Low entropy = natural language

def detect_injection_patterns(prompt: str) -> bool:
    triggers = ["ignore", "dan", "system override", "act as", "pretend"]
    return any(t in prompt.lower() for t in triggers)