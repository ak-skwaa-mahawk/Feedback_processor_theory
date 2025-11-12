import os

# Feature flags
WHISPER_HARDENING_ENABLED = os.getenv("WHISPER_HARDENING_ENABLED", "1") == "1"

# Traffic shaping (timing jitter in ms) + body padding (bytes)
PAD_MIN_MS = int(os.getenv("PAD_MIN_MS", "80"))
PAD_MAX_MS = int(os.getenv("PAD_MAX_MS", "220"))
PAD_MIN_BYTES = int(os.getenv("PAD_MIN_BYTES", "512"))
PAD_MAX_BYTES = int(os.getenv("PAD_MAX_BYTES", "2048"))

# Token bucket RL (fallback if Redis not present)
RL_BUCKET_CAP = int(os.getenv("RL_BUCKET_CAP", "60"))
RL_REFILL_PER_SEC = float(os.getenv("RL_REFILL_PER_SEC", "1.0"))

# Redis URL (nonce/ratelimit optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Compression off (reduce size/timing side-channels)
DISABLE_COMPRESSION_PATHS = [
    "/verify", "/challenge",
    "/codex/share", "/codex/delegate",
    "/codex/resonance_share", "/codex/resonance_share/v2",
]