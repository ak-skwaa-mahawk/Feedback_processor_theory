import os

# Feature flags
WHISPER_HARDENING_ENABLED = os.getenv("WHISPER_HARDENING_ENABLED", "1") == "1"

# Traffic shaping / padding (ms)
PAD_MIN_MS = int(os.getenv("PAD_MIN_MS", "80"))     # min added latency
PAD_MAX_MS = int(os.getenv("PAD_MAX_MS", "220"))    # max added latency

# Response size padding (bytes)
PAD_MIN_BYTES = int(os.getenv("PAD_MIN_BYTES", "512"))
PAD_MAX_BYTES = int(os.getenv("PAD_MAX_BYTES", "2048"))

# Token bucket rate limit (fallback if SlowAPI/Redis not present)
RL_BUCKET_CAP = int(os.getenv("RL_BUCKET_CAP", "60"))       # requests
RL_REFILL_PER_SEC = float(os.getenv("RL_REFILL_PER_SEC", "1.0"))

# Redis URL (nonce/ratelimit optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Disable compression for sensitive endpoints at the app layer too
DISABLE_COMPRESSION_PATHS = ["/verify", "/codex/share", "/codex/delegate", "/codex/resonance_share", "/codex/resonance_share/v2"]