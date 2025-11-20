--- a/src/fireseed/engine.py
+++ b/src/fireseed/engine.py
@@ -1,8 +1,13 @@
 import time
 from .config import settings
 from .ledger import Ledger
 from .income_predictor import Pulse
 from .observers.file_sink import FileSink
 from .observers.console import log as clog
+
+# NEW:
+from .infra import safe_post, auto_adjust_mode_from_health, get_mode
+from .remote import post_record
 
 
 def run():
-    clog("🔥 Fireseed demo starting…")
+    clog(f"🔥 Fireseed demo starting… (infra_mode={get_mode()})")
     led = Ledger(settings.ledger_path)
     fsink = FileSink(settings.log_path)
     pulse = Pulse(seed=settings.seed)
@@ -11,15 +16,34 @@ def run():
     dt = 1.0 / settings.pulse_rate_hz
     t_start = time.time()
     t_end = t_start + settings.run_seconds
     total = 0.0
     recent: list[float] = []
+    last_health_check = t_start
+    health_interval = 30.0  # seconds between infra health checks
 
     while time.time() < t_end:
         rec = pulse.step()
-        led.append(rec)
+        # 1. Ledger is always written first (ground truth)
+        led.append(rec)
+
         amt = rec["amount"]
         total += amt
         recent.append(amt)
         if len(recent) > 20:
             recent.pop(0)
 
         msg = f"tick amount={amt:.2f} total={total:.2f}"
         fsink.log(msg)
         clog(msg)
+
+        # 2. Periodic infra health check → mode auto-adjust
+        now = time.time()
+        if now - last_health_check >= health_interval:
+            mode_after = auto_adjust_mode_from_health()
+            clog(f"[infra] health check → mode={mode_after}")
+            last_health_check = now
+
+        # 3. Safe outbound call (if configured)
+        safe_post(
+            {
+                "kind": "pulse",
+                "amount": amt,
+                "total": total,
+            },
+            post_func=post_record,
+        )
 
         time.sleep(dt)
 
-    clog(f"✅ Fireseed finished. total={total:.2f}")
+    clog(f"✅ Fireseed finished. total={total:.2f}")