git apply <<'PATCH'
*** Begin Patch
*** Add File: Makefile
+# ------------------------------
+# Space Stewardship Compact Makefile
+# ------------------------------
+
+.PHONY: verify-ssc summarize-ssc join-ssc withdraw-ssc
+
+# Verify the last handshake entry for SSC compliance
+verify-ssc:
+	@echo "🔍 Verifying last SSC handshake..."
+	@tail -n 1 logs/handshake_log.json | python tools/handshake_cli.py verify
+
+# Summarize handshake events by subsystem/phase
+summarize-ssc:
+	@echo "📊 Generating SSC summary (CSV)..."
+	@python tools/handshake_summary.py --log logs/handshake_log.json --out logs/summary.csv
+	@echo "✅ Summary written to logs/summary.csv"
+
+# Join the SSC (entity env var required)
+join-ssc:
+ifndef ENTITY
+	$(error Usage: make join-ssc ENTITY=YourOrg)
+endif
+	@python tools/handshake_cli.py log --seed "SSC:join|entity=$(ENTITY)"
+	@echo "✨ Join handshake emitted for $(ENTITY)"
+
+# Withdraw from SSC (entity env var required)
+withdraw-ssc:
+ifndef ENTITY
+	$(error Usage: make withdraw-ssc ENTITY=YourOrg)
+endif
+	@python tools/handshake_cli.py log --seed "SSC:withdraw|entity=$(ENTITY)"
+	@echo "⚠️ Withdrawal handshake emitted for $(ENTITY)"
*** End Patch
PATCH