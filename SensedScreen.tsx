import { RitualOverlay } from "../components/RitualOverlay";
import { useState } from "react";

const SensedScreen = () => {
  const [ritualVisible, setRitualVisible] = useState(false);

  const startRitual = () => {
    setRitualVisible(true);
  };

  const completeRitual = async () => {
    setRitualVisible(false);
    await performRevocation(); // your existing revocation logic
    navigation.navigate("Revoked");
  };

  return (
    <>
      {/* ... existing screen ... */}
      <Button title="Withdraw This Stream" onPress={startRitual} color="#ff4444" />

      <RitualOverlay
        visible={ritualVisible}
        onComplete={completeRitual}
        onCancel={() => setRitualVisible(false)}
      />
    </>
  );
};
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