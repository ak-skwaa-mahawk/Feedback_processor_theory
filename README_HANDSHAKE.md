# from repo root
git apply <<'PATCH'
*** Begin Patch
*** Add File: README_HANDSHAKE.md
+# Handshake System – Two Mile Solutions LLC / Feedback Processor Theory
+
+This document explains how the **Handshake Return System** works inside `Feedback_processor_theory`.
+
+---
+
+## 🧱 Purpose
+
+Every significant event in the Feedback Processor Theory (FPT) runtime—boot, feedback cycle, model update, commit—is cryptographically logged.  
+The `handshake_message()` utility issues a **receipt** that includes:
+
+| Field | Meaning |
+|-------|----------|
+| `entity` | Sovereign root (“TwoMileSolutionsLLC”) |
+| `version` | Handshake protocol version |
+| `timestamp_unix_ms` | Millisecond-precision epoch stamp |
+| `timestamp_iso` | ISO-8601 UTC stamp |
+| `seed` | Descriptive event text |
+| `digest` | SHA-256 hash seal |
+| `node` | Hostname emitting the handshake |
+
+Each receipt is appended to a rolling JSONL file (`logs/handshake_log.json`) forming an immutable ledger.
+
+---
+
+## 🧩 File Layout
+
+```
+Feedback_processor_theory/
+├── fpt/
+│   ├── utils/
+│   │   └── handshake.py          # core logger & verifier
+├── tools/
+│   └── handshake_cli.py          # CLI for manual logging/verification
+├── examples/
+│   └── fpt_handshake_demo.py     # runnable demo
+├── tests/
+│   └── test_handshake.py         # unit test
+├── logs/
+│   └── handshake_log.json        # runtime ledger (auto-created)
+└── .git/hooks/
+    └── post-commit               # git receipt hook (optional)
+```
+
+---
+
+## ⚙️ Usage
+
+### 1 – Emit a Handshake
+```bash
+python tools/handshake_cli.py log --seed "FPT boot|session=alpha01"
+```
+
+### 2 – Verify a Receipt
+```bash
+python tools/handshake_cli.py verify --seed "FPT boot|session=alpha01" < logs/handshake_log.json
+```
+
+### 3 – Auto logging in code
+```python
+from fpt.utils.handshake import handshake_message
+
+def run_cycle(session_id, data):
+    handshake_message(f"FPT:cycle_start:{session_id}")
+    result = process(data)
+    handshake_message(f"FPT:cycle_end:{session_id}|status=ok")
+    return result
+```
+
+### 4 – Git Commit Receipts (optional)
+`.git/hooks/post-commit`
+```bash
+#!/usr/bin/env bash
+seed="GIT:post-commit:$(git rev-parse --short HEAD)"
+python tools/handshake_cli.py log --seed "$seed" >/dev/null 2>&1 || true
+```
+Make it executable:
+```bash
+chmod +x .git/hooks/post-commit
+```
+
+---
+
+## 🔐 Verification Logic
+
+A handshake is valid if:
+
+```python
+payload = f"{entity}|{seed}|{timestamp_unix_ms}|{node}"
+sha256(payload) == digest
+```
+
+This enables independent verification without private keys—integrity through deterministic hashing.
+
+---
+
+## 🧪 Testing
+
+Run the included unit test:
+
+```bash
+pytest tests/test_handshake.py -v
+```
+
+It confirms both generation and verification across saved log lines.
+
+---
+
+## 🗝️ Design Notes
+
+- **Thread-safe**: concurrent writes protected by a lock  
+- **Portable**: pure-Python, no external crypto libs  
+- **Compatible**: works on POSIX + Windows  
+- **Extensible**: swap hash algorithm if needed  
+- **Readable**: JSONL format for append and stream analysis  
+
+---
+
+## 🪶 Integration Ideas
+
+- Tie into **FlameChain** events  
+- Use ledger for **model provenance** / experiment reproducibility  
+- Bridge into **Synara Dashboard** by tailing JSONL stream  
+
+---
+
+## 🧾 License
+
+MIT © 2025 John B. Carroll Jr / Two Mile Solutions LLC  
+Attribution appreciated where derivatives use the handshake protocol.
*** End Patch
PATCH