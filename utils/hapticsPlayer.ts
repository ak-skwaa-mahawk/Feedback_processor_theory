/*
 * Haptic Player — executes patterns based on config
 */

import * as Haptics from "expo-haptics";
import { getCurrentHapticsConfig, HapticIntensity } from "../services/hapticsConfig";

async function playIntensity(intensity: HapticIntensity, style: "selection" | "impact" | "notification") {
  if (intensity === "off") return;

  const map: Record<HapticIntensity, () => Promise<void>> = {
    light: () => Haptics.selectionAsync(),
    medium: () => style === "selection"
      ? Haptics.selectionAsync()
      : style === "impact"
        ? Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
        : Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success),
    heavy: () => style === "impact"
      ? Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)
      : Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),
    off: () => Promise.resolve(),
  };

  await map[intensity]();
}

export async function playBreathStart() {
  const config = getCurrentHapticsConfig();
  await playIntensity(config.breathStart, "notification");
}

export async function playUncoilCue() {
  const config = getCurrentHapticsConfig();
  await playIntensity(config.uncoilCue, "selection");
}

export async function playRitualSuccess() {
  const config = getCurrentHapticsConfig();
  if (config.ritualSuccess === "off") return;

  // Sovereign three-pulse pattern
  await playIntensity(config.ritualSuccess, "notification");
  if (config.ritualSuccess !== "light") {
    setTimeout(() => playIntensity(config.ritualSuccess, "impact"), 200);
    setTimeout(() => playIntensity(config.ritualSuccess, "impact"), 400);
  }
}

export async function playRitualCancel() {
  const config = getCurrentHapticsConfig();
  await playIntensity(config.ritualCancel, "notification");
}

export async function playAuthWarning() {
  const config = getCurrentHapticsConfig();
  await playIntensity(config.authWarning, "notification");
}