import { View, Text, StyleSheet } from "react-native";
import type { Il7State } from "../types";

interface Props {
  il7State: Il7State;
}

export function StatusStrip({ il7State }: Props) {
  const addon =
    il7State === "UNSENSED"
      ? "No EEG is active."
      : il7State === "SENSED"
      ? "You can withdraw this stream at any time."
      : "This stream is frozen; no future use.";

  return (
    <View style={styles.container}>
      <Text style={styles.text}>EEG is never a key. {addon}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 8, backgroundColor: "#f0f0f0", alignItems: "center" },
  text: { fontSize: 12, color: "#444", fontStyle: "italic" },
});