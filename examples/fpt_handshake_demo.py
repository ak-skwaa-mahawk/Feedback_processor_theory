git apply <<'PATCH'
*** Begin Patch
*** Add File: examples/fpt_handshake_demo.py
+from fpt.utils.handshake import handshake_message
+
+def main():
+    handshake_message("FPT:demo:start")
+    # ... do work ...
+    handshake_message("FPT:demo:end|status=ok")
+
+if __name__ == "__main__":
+    main()
*** End Patch
PATCH