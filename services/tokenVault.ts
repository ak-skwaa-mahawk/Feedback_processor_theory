/*
 * Secure Revocation Token Vault
 * Bound by Codex.Legis.Neurodata.v1 §4 — Right to Recoil
 */

import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";
import { Platform } from "react-native";

const TOKEN_KEY_PREFIX = "sovereign_coil_revocation_token_";

export interface VaultedToken {
  sessionId: string;
  token: string;                // human-readable, e.g. "R7-abcd1234"
  tokenHash: string;            // SHA-256, sent to registry
  createdAt: string;
  exportedAt?: string;
}

// Generate a new token for a session
export async function generateAndStoreToken(sessionId: string): Promise<VaultedToken> {
  const token = `R7-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
  const tokenHash = require("crypto-js/sha256")(token).toString();

  const vaulted: VaultedToken = {
    sessionId,
    token,
    tokenHash,
    createdAt: new Date().toISOString(),
  };

  const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;
  await SecureStore.setItemAsync(key, JSON.stringify(vaulted), {
    requireAuthentication: true, // iOS/Android biometric prompt on access
    authenticationPrompt: "Authenticate to access revocation token",
  });

  return vaulted;
}

// Retrieve token — with biometric gate
export async function getTokenWithAuth(sessionId: string): Promise<VaultedToken | null> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();

  const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;

  const options: SecureStore.SecureStoreOptions = {};
  if (hasHardware && isEnrolled && Platform.OS !== "web") {
    // Require biometric every access
    options.requireAuthentication = true;
    options.authenticationPrompt = "Authenticate to reveal revocation token";
  }

  try {
    const stored = await SecureStore.getItemAsync(key, options);
    if (!stored) return null;
    return JSON.parse(stored);
  } catch (e) {
    console.warn("Token access denied or failed");
    return null;
  }
}

// List all stored sessions (no auth needed for list)
export async function listVaultedSessions(): Promise<{ sessionId: string; createdAt: string }[]> {
  const keys = await SecureStore.getAllKeysAsync();
  const coilKeys = keys.filter(k => k.startsWith(TOKEN_KEY_PREFIX));

  const sessions = [];
  for (const key of coilKeys) {
    try {
      const value = await SecureStore.getItemAsync(key);
      if (value) {
        const parsed = JSON.parse(value);
        sessions.push({
          sessionId: parsed.sessionId,
          createdAt: parsed.createdAt,
        });
      }
    } catch {}
  }
  return sessions;
}

// Export token as receipt (no longer requires auth after export)
export async function exportTokenReceipt(sessionId: string): Promise<VaultedToken | null> {
  const token = await getTokenWithAuth(sessionId);
  if (token) {
    token.exportedAt = new Date().toISOString();
    // Optionally mark as exported in storage (or delete after export)
  }
  return token;
}

// Optional: delete after successful revocation
export async function deleteToken(sessionId: string): Promise<void> {
  const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;
  await SecureStore.deleteItemAsync(key);
}