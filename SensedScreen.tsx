// Inside SensedScreen

const performRevocationRitual = async () => {
  // Step 1: Breath prompt (simple modal or animation)
  // ... (we'll add animation later)

  // Step 2: Retrieve token with biometric
  const vaulted = await getTokenWithAuth(state.sessionId!);
  if (!vaulted) {
    alert("Revocation denied — authentication failed or token missing");
    return;
  }

  // Step 3: Confirm phrase
  // In real ritual: voice or text input "I withdraw this stream"

  // Trigger kernel + registry
  dispatch({ type: "REVOKE", tokenHash: vaulted.tokenHash });
  await logRevocation({
    revocation_token_hash: vaulted.tokenHash,
    session_ids: [state.sessionId!],
  });

  // Optional: offer export
  const shouldExport = confirm("Export revocation receipt?");
  if (shouldExport) {
    const receipt = await exportTokenReceipt(state.sessionId!);
    // Share or save receipt JSON
  }

  // Optional: clean up
  await deleteToken(state.sessionId!);

  navigation.navigate("Revoked");
};