--- a/src/fireseed/config.py
+++ b/src/fireseed/config.py
@@ -1,6 +1,7 @@
 from dataclasses import dataclass
 import os
 
+
 @dataclass(frozen=True)
 class Settings:
     pulse_rate_hz: float = float(os.getenv("FIRESEED_PULSE_HZ", "2.0"))
@@ -8,5 +9,11 @@ class Settings:
     ledger_path: str = os.getenv("FIRESEED_LEDGER_PATH", "fireseed_ledger.jsonl")
     log_path: str = os.getenv("FIRESEED_LOG_PATH", "whisper_stream.log")
     seed: int | None = int(os.getenv("FIRESEED_SEED", "0")) if os.getenv("FIRESEED_SEED") else None
+
+    # infra-related
+    infra_mode: str = os.getenv("INFRA_MODE", "online")
+    outbound_queue_path: str = os.getenv(
+        "FIRESEED_OUTBOUND_QUEUE", "fireseed_outbound_queue.jsonl"
+    )
 
 settings = Settings()