git apply <<'PATCH'
*** Begin Patch
*** Add File: fpt/utils/decorators.py
+from functools import wraps
+from fpt.utils.hs import hs
+
+def handshake_step(subsys: str, name: str):
+    """
+    Decorate any function to emit pre/post/error receipts automatically.
+      @handshake_step("ISST","coherence_eval")
+      def evaluate_coherence(...): ...
+    """
+    def deco(fn):
+        @wraps(fn)
+        def _w(*args, **kwargs):
+            hs(subsys, "pre", step=name)
+            try:
+                out = fn(*args, **kwargs)
+                hs(subsys, "post", step=name, ok=True)
+                return out
+            except Exception as e:
+                hs(subsys, "error", step=name, msg=type(e).__name__)
+                raise
+        return _w
+    return deco
+
*** End Patch
PATCH
from functools import wraps
from fpt.utils.hs import hs

def handshake_step(subsys: str, name: str):
    def deco(fn):
        @wraps(fn)
        def _w(*args, **kwargs):
            hs(subsys, "pre", step=name)
            try:
                out = fn(*args, **kwargs)
                hs(subsys, "post", step=name, ok=True)
                return out
            except Exception as e:
                hs(subsys, "error", step=name, msg=type(e).__name__)
                raise
        return _w
    return deco