/*
 * Edge Case Tests: Vault & Logger Resilience
 */

import { generateAndStoreToken, listVaultedSessions } from "../services/tokenVault";
import { logger } from "../services/logger";
import * as SecureStore from "expo-secure-store";

const mockLog = jest.fn();
beforeAll(() => {
  Object.defineProperty(logger, "log", { value: mockLog, writable: true });
});

describe("Vault Edge Cases", () => {
  test("concurrent session token generation — no collision", async () => {
    const sessions = ["edge-1", "edge-2", "edge-3"];
    const tokens = await Promise.all(sessions.map(s => generateAndStoreToken(s)));

    const uniqueHashes = new Set(tokens.map(t => t.tokenHash));
    expect(uniqueHashes.size).toBe(3); // no hash collision

    const uniqueTokens = new Set(tokens.map(t => t.token));
    expect(uniqueTokens.size).toBe(3);
  });

  test("listVaultedSessions skips corrupted entries gracefully", async () => {
    await generateAndStoreToken("good-session");

    (SecureStore.getAllKeysAsync as jest.Mock).mockResolvedValue([
      "sovereign_coil_revocation_token_good-session",
      "sovereign_coil_revocation_token_corrupt",
    ]);

    (SecureStore.getItemAsync as jest.Mock)
      .mockResolvedValueOnce(JSON.stringify({ sessionId: "good-session", createdAt: "2025" })) // good
      .mockResolvedValueOnce("{ invalid json }"); // corrupt

    const list = await listVaultedSessions();

    expect(list).toHaveLength(1);
    expect(list[0].sessionId).toBe("good-session");

    expect(mockLog).toHaveBeenCalledWith("WARN", "Skipping corrupted vault entry during listing", expect.any(Object));
  });

  test("logger sanitizeContext blocks attempted neurodata leak", () => {
    const dangerous = {
      token: "R7-LEAKME12",
      raw_eeg: new Array(1000).fill(0.001),
      vitality: 1.2,
    };

    const loggerAny = logger as any;
    const sanitized = loggerAny.sanitizeContext(dangerous);

    expect(sanitized.token).toMatch(/\*\*\*\*/);
    expect(sanitized.raw_eeg).toBe("[REDACTED_NEURODATA]");
    expect(sanitized.vitality).toBe(1.2);
  });
});