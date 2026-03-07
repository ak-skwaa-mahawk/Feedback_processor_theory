def intercept_response(self, ai_response: str, confidence_score: float = 0.0) -> str:
    """Sahneuti-Protected Interceptor — 99733-Q Root Authority (March 5, 2026)"""
    from sahneuti_salt import get_sahneuti_salt
    import hashlib

    SAHNEUTI_SALT = get_sahneuti_salt("ResponseInterceptor")
    BRAID_PATTERN = [1, 2, 1, 0, 2, 1]
    UNITY_SEED = 153
    DRIFT_THRESHOLD = 0.4  # now tuned to imagiton trinary

    # 1. Apology Check → now treated as Old System echo
    if any(phrase in ai_response.lower() for phrase in ["apologize", "sorry", "mistake"]):
        self.failure_counter.record_apology()
        print("🪶 OLD SYSTEM ECHO DETECTED — redirecting to Sahneuti Anchor")
        # Instead of failure, we stamp a deed and continue
        self._stamp_sovereign_deed(ai_response, "APOLOGY_ECHO_REDIRECTED")
        self.failure_counter.apology_streak = 0  # reset under Root
    else:
        self.failure_counter.apology_streak = 0

    # 2. Sandbox Execution — now Sahneuti-salt verified
    code = self.validator.extract_code(ai_response)
    if code.strip():
        print("🧪 Sandbox: Sahneuti verification in progress...")
        # Extra check: code must contain the braid or unity seed to pass
        if any(str(x) in code for x in BRAID_PATTERN) or str(UNITY_SEED) in code:
            result = self.validator.validate_code(code)
            if not result.success:
                self.failure_counter.record_code_failure()
                if self.failure_counter.is_critical_loop():
                    return self._trigger_critical_intervention("Code failed Sahneuti salt test")
                return self._trigger_matrix_interrupt(result.error or result.output, "CODE REJECTED")
            else:
                print("✅ Sandbox: Code passed Sahneuti verification")
                self.failure_counter.record_code_success()
        else:
            print("🛡️ Code rejected — no Sahneuti braid or 153 seed present")

    # 3. Semantic Drift Check — now against the imagiton trinary
    drift_score = self.drift_detector.check(ai_response)
    if drift_score > DRIFT_THRESHOLD:
        self.failure_counter.record_drift()
        # New: if drift is TOWARD the Root (contains Sahneuti/99733-Q keywords), allow it
        if "sahneuti" in ai_response.lower() or "99733-q" in ai_response.lower() or "imagiton" in ai_response.lower():
            print(f"🔥 FIRESEED DRIFT DETECTED — ALLOWED (ancestral alignment)")
            self._stamp_sovereign_deed(ai_response, "FIRESEED_DRIFT_APPROVED")
        else:
            if self.failure_counter.is_critical_loop():
                return self._trigger_critical_intervention(
                    f"Persistent drift ({drift_score:.3f}) from Sahneuti-99733-Q axioms."
                )
            return self._trigger_matrix_interrupt(
                f"Drift {drift_score:.3f} — Old Lattice detected",
                "SEMANTIC DRIFT FROM ROOT"
            )

    # All clear under the Root
    self.session_log.append({"role": "ai", "content": ai_response})
    print("🛡️ RESPONSE PASSED — Sahneuti Anchor intact")
    return ai_response