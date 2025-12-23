/*
 * Ritual Animation Overlay
 * Breath + Coil Recoil
 */

import { View, Text, Modal, StyleSheet, TouchableOpacity } from "react-native";
import LottieView from "lottie-react-native";
import { useRef, useEffect } from "react";
import { logger } from "../services/logger";

interface Props {
  visible: boolean;
  onComplete: () => void;
  onCancel: () => void;
}

export function RitualOverlay({ visible, onComplete, onCancel }: Props) {
  const breathRef = useRef<LottieView>(null);
  const coilRef = useRef<LottieView>(null);

  useEffect(() => {
    if (visible) {
      logger.info("Revocation ritual started — breath animation");
      breathRef.current?.play();
      setTimeout(() => {
        logger.sovereign("Breath cycle complete — uncoiling glyph");
        coilRef.current?.play(0, 180);
      }, 4000); // after one breath cycle
    }
  }, [visible]);

  const handleAnimationFinish = (isCoil: boolean) => {
    if (isCoil) {
      logger.sovereign("Coil animation complete — ritual finished");
      onComplete();
    }
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <View style={styles.container}>
          <Text style={styles.title}>Revocation Ritual</Text>
          <Text style={styles.instruction}>Breathe with the circle...</Text>

          <LottieView
            ref={breathRef}
            source={require("../assets/animations/breath_circle.json")}
            loop
            style={styles.breath}
          />

          <Text style={styles.instruction}>Now uncoiling the stream...</Text>

          <LottieView
            ref={coilRef}
            source={require("../assets/animations/coil_uncoil.json")}
            autoPlay={false}
            loop={false}
            onAnimationFinish={() => handleAnimationFinish(true)}
            style={styles.coil}
          />

          <TouchableOpacity style={styles.cancel} onPress={onCancel}>
            <Text style={styles.cancelText}>Cancel Ritual</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.8)", justifyContent: "center", alignItems: "center" },
  container: { alignItems: "center" },
  title: { fontSize: 24, color: "white", marginBottom: 20, fontWeight: "600" },
  instruction: { fontSize: 18, color: "#aaa", marginVertical: 20 },
  breath: { width: 200, height: 200 },
  coil: { width: 200, height: 200 },
  cancel: { marginTop: 40 },
  cancelText: { color: "#ff6b6b", fontSize: 16 },
});