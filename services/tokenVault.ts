/*
 * Secure Revocation Token Vault — v1.2.0
 * Fully logged, sovereign acts witnessed
 */

import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";
import { Platform } from "react-native";
import CryptoJS from "crypto-js";
import { logger } from "./logger";  // ← Integrated

const TOKEN_KEY_PREFIX = "sovereign_coil_revocation_token_";

export interface VaultedToken {
  sessionId: string;
  token: string;
  tokenHash: string;
  createdAt: string;
  exportedAt?: string;
}

export class TokenVaultError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = "TokenVaultError";
  }
}

export async function generateAndStoreToken(sessionId: string): Promise<VaultedToken> {
  try {
    if (!sessionId || typeof sessionId !== "string") {
      logger.warn("Attempted token generation with invalid session ID");
      throw new TokenVaultError("INVALID_SESSION", "Valid session ID required");
    }

    const token = `R7-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
    const tokenHash = CryptoJS.SHA256(token).toString();

    const vaulted: VaultedToken = {
      sessionId,
      token,
      tokenHash,
      createdAt: new Date().toISOString(),
    };

    const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;

    logger.info("Storing new revocation token", {
      sessionId,
      tokenPreview: `${token.slice(0, 6)}****`,
    });

    await SecureStore.setItemAsync(key, JSON.stringify(vaulted), {
      keychainAccessible: SecureStore.ALWAYS_THIS_DEVICE_ONLY,
    });

    logger.sovereign("Revocation token generated and vaulted", { sessionId });

    return vaulted;
  } catch (err) {
    if (err instanceof TokenVaultError) throw err;

    logger.error("Failed to generate/store revocation token", {
      sessionId,
      error: err instanceof Error ? err.message : String(err),
    });

    throw new TokenVaultError(
      "STORAGE_FAILURE",
      "Could not securely store revocation token — sovereignty boundary preserved"
    );
  }
}

export async function getTokenWithAuth(sessionId: string): Promise<VaultedToken | null> {
  try {
    if (!sessionId) {
      logger.warn("Token retrieval attempted without session ID");
      throw new TokenVaultError("MISSING_SESSION", "Session ID required");
    }

    const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;

    logger.info("Requesting revocation token from vault", { sessionId });

    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();

    const options: SecureStore.SecureStoreOptions = {
      keychainAccessible: SecureStore.ALWAYS_THIS_DEVICE_ONLY,
    };

    if (hasHardware && isEnrolled && Platform.OS !== "web") {
      options.requireAuthentication = true;
      options.authenticationPrompt = {
        title: "Revoke Stream",
        subtitle: "Authenticate to access revocation token",
        description: "Your nervous system boundary requires confirmation",
      };
    }

    const stored = await SecureStore.getItemAsync(key, options);

    if (!stored) {
      logger.warn("No revocation token found in vault", { sessionId });
      return null;
    }

    let parsed: VaultedToken;
    try {
      parsed = JSON.parse(stored) as VaultedToken;
    } catch (parseErr) {
      logger.error("Corrupted token data in vault", { sessionId });
      throw new TokenVaultError("CORRUPT_DATA", "Stored token corrupted");
    }

    logger.sovereign("Revocation token accessed successfully", {
      sessionId,
      tokenPreview: `${parsed.token.slice(0, 6)}****`,
    });

    return parsed;
  } catch (err) {
    if (err instanceof TokenVaultError) throw err;

    if (err.name === "AuthenticationError" || String(err).includes("cancelled")) {
      logger.info("User cancelled token authentication", { sessionId });
      throw new TokenVaultError("AUTH_CANCELLED", "Authentication cancelled — stream remains active");
    }

    logger.error("Token retrieval failed", {
      sessionId,
      error: err instanceof Error ? err.message : String(err),
    });

    throw new TokenVaultError(
      "ACCESS_DENIED",
      "Could not access revocation token — sovereignty preserved"
    );
  }
}

export async function listVaultedSessions(): Promise<{ sessionId: string; createdAt: string }[]> {
  try {
    logger.debug("Listing vaulted sessions");

    const keys = await SecureStore.getAllKeysAsync();
    const coilKeys = keys.filter(k => k.startsWith(TOKEN_KEY_PREFIX));

    const sessions = [];
    for (const key of coilKeys) {
      try {
        const value = await SecureStore.getItemAsync(key);
        if (value) {
          const parsed = JSON.parse(value);
          if (parsed.sessionId && parsed.createdAt) {
            sessions.push({
              sessionId: parsed.sessionId,
              createdAt: parsed.createdAt,
            });
          }
        }
      } catch (e) {
        logger.warn("Skipping corrupted vault entry during listing", { key });
      }
    }

    logger.info("Vault session list complete", { count: sessions.length });
    return sessions;
  } catch (err) {
    logger.error("Failed to list vaulted sessions", { error: err });
    return [];
  }
}

export async function exportTokenReceipt(sessionId: string): Promise<VaultedToken | null> {
  try {
    logger.info("Exporting revocation receipt", { sessionId });

    const token = await getTokenWithAuth(sessionId);
    if (token) {
      token.exportedAt = new Date().toISOString();
      logger.sovereign("Revocation receipt exported", { sessionId });
    }
    return token;
  } catch (err) {
    if (err instanceof TokenVaultError) {
      logger.warn("Receipt export failed", { sessionId, code: err.code });
      throw err;
    }
    logger.error("Unexpected error during receipt export", { sessionId });
    throw new TokenVaultError("EXPORT_FAILED", "Could not export receipt");
  }
}

export async function deleteToken(sessionId: string): Promise<void> {
  try {
    const key = `\( {TOKEN_KEY_PREFIX} \){sessionId}`;
    await SecureStore.deleteItemAsync(key);

    logger.sovereign("Revocation token securely deleted from vault", { sessionId });
  } catch (err) {
    logger.error("Failed to delete revocation token", { sessionId, error: err });
    throw new TokenVaultError("DELETE_FAILED", "Could not fully delete token");
  }
}