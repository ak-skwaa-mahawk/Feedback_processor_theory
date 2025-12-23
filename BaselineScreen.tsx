// BaselineScreen.tsx
import { View, Text, Button, StyleSheet } from "react-native";
import { useIl7Kernel } from "../hooks/useIl7Kernel";
import { StatusStrip } from "../components/StatusStrip";
import { v4 as uuidv4 } from "uuid";
import CryptoJS from "crypto-js"; // expo install crypto-js

export function BaselineScreen({ navigation }: any) {
  const { state, dispatch } = useIl7Kernel();

  const startSession = () => {
    const sessionId = `sess-${uuidv4().slice(0, 8)}`;
    const token = `R7-${Math.random().toString(36).slice(2, 10)}`;
    const tokenHash = CryptoJS.SHA256(token).toString();
    dispatch({ type: "START_SENSED", sessionId, tokenHash });
    navigation.navigate("Sensed");
  };

  return (
    <View style={styles.container}>
      <Text style={styles.glyph}>⟲</Text>
      <Text style={styles.title}>Your nervous system is at rest.</Text>
      <Text>Surplus flows at baseline (ε_d = 0.0417).</Text>
      <Button title="Start Sensed Session" onPress={startSession} />
      <StatusStrip il7State={state.il7State} />
    </View>
  );
}

// SensedScreen.tsx (abridged)
export function SensedScreen({ navigation }: any) {
  const { state, dispatch } = useIl7Kernel();
  // ... vitality gauge, band display, etc.

  const revoke = () => {
    // In real ritual flow, collect breath/phrase first
    dispatch({ type: "REVOKE", tokenHash: state.revocationTokenHash! });
    mockLogRevocation({ sessionId: state.sessionId, action: "stop_future_use" });
    navigation.navigate("Revoked");
  };

  return (
    <View style={styles.container}>
      <Text style={styles.glyph}>⟲·</Text>
      <Text>Vitality: {state.vitality.toFixed(3)}</Text>
      <Text>ε_d: {state.epsilonD.toFixed(4)}</Text>
      <Button title="Withdraw This Stream" onPress={revoke} color="red" />
      <StatusStrip il7State={state.il7State} />
    </View>
  );
}

// RevokedScreen.tsx (transient)
export function RevokedScreen({ navigation }: any) {
  const { state } = useIl7Kernel();

  useEffect(() => {
    const timer = setTimeout(() => navigation.navigate("Baseline"), 8000);
    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <View style={styles.container}>
      <Text style={styles.glyph}>⟲·//</Text>
      <Text style={styles.title}>Revocation Honored</Text>
      <Text>EEG influence has recoiled.</Text>
      <Text>This stream is now frozen testimony.</Text>
      <StatusStrip il7State="REVOKED" />
    </View>
  );
}