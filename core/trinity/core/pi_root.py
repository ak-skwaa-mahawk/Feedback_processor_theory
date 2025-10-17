diff --git a/core/pi_root.py b/core/pi_root.py
new file mode 100644
index 0000000..abcdef0
--- /dev/null
+++ b/core/pi_root.py
@@ -0,0 +1,60 @@
+import math
+from typing import Callable, Optional
+
+# Correction function for π, default is no change
+_pi_correction_fn: Optional[Callable[[float], float]] = None
+
+def set_pi_correction(fn: Optional[Callable[[float], float]]):
+    """
+    Set a correction function for π. Takes math.pi → float.
+    Pass None to disable correction (use raw pi).
+    """
+    global _pi_correction_fn
+    _pi_correction_fn = fn
+
+def get_pi_base() -> float:
+    """Return raw math.pi (base value)."""
+    return math.pi
+
+def pi_root() -> float:
+    """
+    Return the effective π used across system.
+    If a correction function is set, apply it; otherwise, return math.pi.
+    """
+    if _pi_correction_fn is None:
+        return math.pi
+    try:
+        return float(_pi_correction_fn(math.pi))
+    except Exception:
+        # Fall back safely
+        return math.piimport math

# optional correction hooks
try:
    from core.trinity.correction import kappa_over_pi_correction, describe as trinity_desc
except ImportError:
    kappa_over_pi_correction = None
    trinity_desc = lambda: "Trinity correction unavailable"

_pi_correction_fn = None

def set_pi_correction(fn):
    """Register external π-correction function."""
    global _pi_correction_fn
    _pi_correction_fn = fn

def pi_root() -> float:
    """
    Returns the corrected π constant.
    Priority:
      1. Trinity κ/π correction (if available)
      2. User-registered correction
      3. Default math.pi
    """
    base = math.pi
    if kappa_over_pi_correction:
        return float(kappa_over_pi_correction(base))
    if _pi_correction_fn:
        try:
            return float(_pi_correction_fn(base))
        except Exception:
            pass
    return base

def status():
    """Human-readable status for dashboards or logs."""
    return {
        "base_pi": math.pi,
        "corrected_pi": pi_root(),
        "correction_source": "Trinity κ/π" if kappa_over_pi_correction else "User / Default",
        "note": trinity_desc()
    }

diff --git a/core/feedback_logger.py b/core/feedback_logger.py
index 1234567..89abcd0 100644
--- a/core/feedback_logger.py
+++ b/core/feedback_logger.py
@@ -1,5 +1,7 @@
 import json, datetime, os, hashlib
-from math import pi
+from core.pi_root import pi_root
+
 def log_feedback(conversation, output_dir="data/resonance_logs"):
     os.makedirs(output_dir, exist_ok=True)
     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
     log = {
         "timestamp": timestamp,
         "conversation": conversation,
         "length": len(conversation),
         "speakers": list(set([x[0] for x in conversation])),
-        "pi_feedback_constant": pi
+        "pi_feedback_constant": pi_root()
     }
     file_path = f"{output_dir}/resonance_log_{timestamp}.json"
     with open(file_path, "w") as f:
         json.dump(log, f, indent=4)
     return file_path

 def log_metadata(event, data, output_dir="data/resonance_logs"):
     os.makedirs(output_dir, exist_ok=True)
     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
     passcode = data.get("passcode", "")
-    hashed = hashlib.sha256((passcode + str(pi)).encode()).hexdigest()
+    hashed = hashlib.sha256((passcode + str(pi_root())).encode()).hexdigest()
     data.update({
         "hashed_passcode": hashed,
         "event": event,
         "timestamp": timestamp,
-        "pi_feedback_constant": pi
+        "pi_feedback_constant": pi_root()
     })
     file_path = f"{output_dir}/metadata_{timestamp}.json"
     with open(file_path, "w") as f:
         json.dump(data, f, indent=4)
     return file_path

diff --git a/core/feedback_spectrogram.py b/core/feedback_spectrogram.py
index abcdef0..fedcba9 100644
--- a/core/feedback_spectrogram.py
+++ b/core/feedback_spectrogram.py
@@ -1,5 +1,7 @@
 import numpy as np
 import matplotlib.pyplot as plt
 from scipy.signal import spectrogram
-import os, datetime, json
+import os, datetime, json
+from core.pi_root import pi_root

 def validate_passcode(passcode):
     return passcode == "XHT-421-FlameDrop"

 def feedback_spectrogram(conversation, passcode, output_dir="data/spectrograms"):
     if not validate_passcode(passcode):
         return "Whisper’s listening. Invalid passcode—flame clearance denied."
     os.makedirs(output_dir, exist_ok=True)
     energy_map = {'🔥': 1.0, '😎': 0.8, '!': 0.7, '?': 0.6, 'kin': 0.5, 'loop': 0.4, 'push': 0.3, '(': 0.2, '.': 0.1}
     signal = []
     for speaker, text in conversation:
         tokens = text.split()
         value = sum(energy_map.get(tok, 0.05) for tok in tokens)
         signal.append(value if speaker == "You" else 0.8 * value)
     if len(signal) > 1000:
         signal = signal[:1000]
     fs = 10
     f, t, Sxx = spectrogram(signal, fs)
     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
     filename = f"{output_dir}/spectrogram_{timestamp}.png"
     plt.figure(figsize=(8,4))
     plt.pcolormesh(t, f, Sxx, shading='gouraud')
-    plt.title("Conversational Resonance Spectrogram (XHT-421-FlameDrop)")
+    plt.title(f"Conversational Resonance Spectrogram (XHT-421-FlameDrop) — π*={pi_root():.6f}")
     plt.xlabel("Dialogue Time (turns)")
     plt.ylabel("Frequency (semantic intensity)")
     plt.savefig(filename, dpi=300)
     plt.close()
     return filename