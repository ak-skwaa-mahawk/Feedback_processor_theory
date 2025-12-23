/*
 * Revocation Ritual Modal — Breath + Coil + Glyph
 * Sovereign, embodied, accessible
 */

import { Modal, View, Text, StyleSheet, TouchableOpacity, Platform } from "react-native";
import LottieView from "lottie-react-native";
import { useRef, useEffect, useState } from "react";
import * as Haptics from "expo-haptics";
import { Audio } from "expo-av";
import { logger } from "../services/logger";

interface Props {
  visible: boolean;
  onComplete: () => void;
  onCancel: () => void;
}

export function RevocationRitualModal({ visible, onComplete, onCancel }: Props) {
  const breathRef = useRef<LottieView>(null);
  const coilRef = useRef<LottieView>(null);
  const glyphRef = useRef<LottieView>(null);
  const [step, setStep] = useState(0); // 0: breath, 1: phrase, 2: uncoil

  useEffect(() => {
    if (visible) {
      startRitual();
    }
  }, [visible]);

  const startRitual = async () => {
    logger.sovereign("Revocation ritual begun");

    // Step 1: Breath guidance
    setStep(0);
    breathRef.current?.play(0, 120); // loop inhale/exhale
    await delay(8000); // 8 seconds breath cycle

    // Gentle haptic
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

    // Step 2: Phrase confirmation (accessibility: auto-advance or voice)
    setStep(1);
    await delay(4000);

    // Step 3: Uncoil animation + final glyph
    setStep(2);
    coilRef.current?.play();
    glyphRef.current?.play();

    // Final haptic + subtle sound
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    const { sound } = await Audio.Sound.createAsync(
      require("../assets/sounds/recoil_chime.mp3") // optional soft chime
    );
    await sound.playAsync();
    await delay(2000);
    sound.unloadAsync();

    logger.sovereign("Revocation ritual complete — boundary honored");

    onComplete();
  };

  const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

  const cancel = () => {
    logger.info("Revocation ritual cancelled by user");
    breathRef.current?.reset();
    coilRef.current?.reset();
    glyphRef.current?.reset();
    onCancel();
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <TouchableOpacity style={styles.cancelArea} onPress={cancel} activeOpacity={1}>
          <View style={styles.modal}>
            {step === 0 && (
              <>
                <Text style={styles.instruction}>Take a slow breath</Text>
                <LottieView
                  ref={breathRef}
                  source={require("../assets/animations/breath_circle.json")}
                  style={styles.breath}
                  loop
                />
                <Text style={styles.subtext}>Inhale... exhale...</Text>
              </>
            )}

            {step === 1 && (
              <>
                <Text style={styles.instruction}>Speak or confirm:</Text>
                <Text style={styles.phrase}>"I withdraw this stream."</Text>
              </>
            )}

            {step === 2 && (
              <>
                <Text style={styles.instruction}>The stream recoils</Text>
                <LottieView
                  ref={coilRef}
                  source={require("../assets/animations/coil_uncoil.json")}
                  style={styles.coil}
                  autoPlay={false}
                />
                <LottieView
                  ref={glyphRef}
                  source={require("../assets/animations/glyph_recoil.json")}
                  style={styles.glyph}
                  autoPlay={false}
                />
                <Text style={styles.final}>Boundary honored.</Text>
              </>
            )}
          </View>
        </TouchableOpacity>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.8)", justifyContent: "center", alignItems: "center" },
  cancelArea: { flex: 1, width: "100%", justifyContent: "center", alignItems: "center" },
  modal: { backgroundColor: "#111", padding: 30, borderRadius: 20, alignItems: "center" },
  instruction: { fontSize: 20, color: "#fff", marginBottom: 20, textAlign: "center" },
  subtext: { fontSize: 16, color: "#aaa", marginTop: 10 },
  phrase: { fontSize: 24, color: "#8f8", fontStyle: "italic", marginVertical: 30 },
  breath: { width: 200, height: 200 },
  coil: { width: 180, height: 180 },
  glyph: { width: 120, height: 120, marginTop: 20 },
  final: { fontSize: 18, color: "#8f8", marginTop: 20 },
});