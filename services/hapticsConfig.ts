/*
 * Customizable Haptic Feedback Configuration
 * Sovereign control over ritual feel
 */

import * as SecureStore from "expo-secure-store"; // or AsyncStorage if preferred

const HAPTICS_CONFIG_KEY = "sovereign_coil_haptics_config";

export type HapticIntensity = "off" | "light" | "medium" | "heavy";

export interface HapticPhaseConfig {
  breathStart: HapticIntensity;
  uncoilCue: HapticIntensity;
  ritualSuccess: HapticIntensity;
  ritualCancel: HapticIntensity;
  authWarning: HapticIntensity;
}

const DEFAULT_CONFIG: HapticPhaseConfig = {
  breathStart: "light",
  uncoilCue: "light",
  ritualSuccess: "medium",
  ritualCancel: "light",
  authWarning: "medium",
};

let currentConfig: HapticPhaseConfig = { ...DEFAULT_CONFIG };

export async function loadHapticsConfig(): Promise<HapticPhaseConfig> {
  try {
    const stored = await SecureStore.getItemAsync(HAPTICS_CONFIG_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      currentConfig = { ...DEFAULT_CONFIG, ...parsed };
    }
  } catch (e) {
    console.warn("Failed to load haptics config — using defaults");
  }
  return currentConfig;
}

export async function saveHapticsConfig(config: HapticPhaseConfig): Promise<void> {
  try {
    await SecureStore.setItemAsync(HAPTICS_CONFIG_KEY, JSON.stringify(config));
    currentConfig = config;
  } catch (e) {
    console.warn("Failed to save haptics config");
  }
}

export function getCurrentHapticsConfig(): HapticPhaseConfig {
  return currentConfig;
}