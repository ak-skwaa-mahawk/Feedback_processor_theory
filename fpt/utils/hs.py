git apply <<'PATCH'
*** Begin Patch
*** Add File: fpt/utils/hs.py
+from fpt.utils.handshake import handshake_message
+
+def hs(subsys: str, phase: str, **kv):
+    """
+    Standardized seed emitter.
+      subsys: BlackBoxDefense | ISST | Synara | FPT | GIT | CI
+      phase : start | end | pre | post | alert | error
+      kv    : optional metadata, logged as k=v pairs
+    """
+    meta = "|".join(f"{k}={v}" for k, v in kv.items()) if kv else ""
+    seed = f"{subsys}:{phase}" + (f"|{meta}" if meta else "")
+    return handshake_message(seed)
+
*** End Patch
PATCH
# Lightweight wrapper to standardize seeds per subsystem
from fpt.utils.handshake import handshake_message

def hs(subsys: str, phase: str, **kv):
    # phase: pre | post | start | end | alert | error
    meta = "|".join(f"{k}={v}" for k, v in kv.items()) if kv else ""
    seed = f"{subsys}:{phase}" + (f"|{meta}" if meta else "")
    return handshake_message(seed)