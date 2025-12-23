/*
 * Integration Tests: Secure Token Vault Full Lifecycle
 * Sovereign acts must be stored, accessed, exported, and deleted correctly
 * All acts must be witnessed by the logger
 */

import { generateAndStoreToken, getTokenWithAuth, exportTokenReceipt, deleteToken, listVaultedSessions } from "../services/tokenVault";
import { logger } from "../services/logger";
import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";

jest.mock("expo-secure-store");
jest.mock("expo-local-authentication");

// Spy on logger
const mockLog = jest.fn();
beforeAll(() => {
  Object.defineProperty(logger, "log", { value: mockLog, writable: true });
});

const TEST_SESSION_1 = "sess-int-1111";
const TEST_SESSION_2 = "sess-int-2222";

beforeEach(() => {
  jest.clearAllMocks();
  mockLog.mockReset();
  (SecureStore.setItemAsync as jest.Mock).mockResolvedValue(undefined);
  (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(undefined);
  (SecureStore.deleteItemAsync as jest.Mock).mockResolvedValue(undefined);
  (LocalAuthentication.hasHardwareAsync as jest.Mock).mockResolvedValue(false);
  (LocalAuthentication.isEnrolledAsync as jest.Mock).mockResolvedValue(false);
});

describe("Token Vault Integration — Full Sovereign Lifecycle", () => {
  test("complete lifecycle: generate → retrieve → export → delete", async () => {
    // Phase 1: Generate & Store
    const token1 = await generateAndStoreToken(TEST_SESSION_1);

    expect(token1.sessionId).toBe(TEST_SESSION_1);
    expect(token1.token).toMatch(/^R7-[A-Z0-9]{8}$/);
    expect(token1.tokenHash).toHaveLength(64);

    expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
      expect.stringContaining(TEST_SESSION_1),
      expect.any(String)
    );

    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token generated and vaulted", { sessionId: TEST_SESSION_1 });

    // Phase 2: Retrieve with auth (no biometrics in test)
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValueOnce(JSON.stringify(token1));

    const retrieved = await getTokenWithAuth(TEST_SESSION_1);

    expect(retrieved).toEqual(token1);
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token accessed successfully", expect.objectContaining({
      sessionId: TEST_SESSION_1,
      tokenPreview: expect.stringMatching(/R7-..\*\*\*\*/),
    }));

    // Phase 3: Export receipt
    const receipt = await exportTokenReceipt(TEST_SESSION_1);

    expect(receipt?.exportedAt).toBeDefined();
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation receipt exported", { sessionId: TEST_SESSION_1 });

    // Phase 4: Delete
    await deleteToken(TEST_SESSION_1);

    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith(expect.stringContaining(TEST_SESSION_1));
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token securely deleted from vault", { sessionId: TEST_SESSION_1 });
  });

  test("multiple sessions coexist and list correctly", async () => {
    const token1 = await generateAndStoreToken(TEST_SESSION_1);
    const token2 = await generateAndStoreToken(TEST_SESSION_2);

    (SecureStore.getAllKeysAsync as jest.Mock).mockResolvedValue([
      `sovereign_coil_revocation_token_${TEST_SESSION_1}`,
      `sovereign_coil_revocation_token_${TEST_SESSION_2}`,
      "other_key",
    ]);

    (SecureStore.getItemAsync as jest.Mock)
      .mockResolvedValueOnce(JSON.stringify(token1))
      .mockResolvedValueOnce(JSON.stringify(token2))
      .mockResolvedValueOnce(null); // other_key

    const list = await listVaultedSessions();

    expect(list).toHaveLength(2);
    expect(list).toContainEqual(expect.objectContaining({ sessionId: TEST_SESSION_1 }));
    expect(list).toContainEqual(expect.objectContaining({ sessionId: TEST_SESSION_2 }));

    expect(mockLog).toHaveBeenCalledWith("INFO", "Vault session list complete", { count: 2 });
  });

  test("corrupted storage triggers ERROR and graceful fallback", async () => {
    await generateAndStoreToken(TEST_SESSION_1);

    // Simulate corrupted JSON on read
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValueOnce("{{{ invalid json }}}");

    await expect(getTokenWithAuth(TEST_SESSION_1)).rejects.toThrow("CORRUPT_DATA");

    expect(mockLog).toHaveBeenCalledWith("ERROR", "Corrupted token data in vault", { sessionId: TEST_SESSION_1 });
  });

  test("storage failure during generation logs ERROR but throws", async () => {
    (SecureStore.setItemAsync as jest.Mock).mockRejectedValueOnce(new Error("keychain unavailable"));

    await expect(generateAndStoreToken(TEST_SESSION_1)).rejects.toThrow("STORAGE_FAILURE");

    expect(mockLog).toHaveBeenCalledWith("ERROR", "Failed to generate/store revocation token", expect.objectContaining({
      sessionId: TEST_SESSION_1,
    }));
  });

  test("missing token on retrieval logs WARN and returns null", async () => {
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValueOnce(null);

    const result = await getTokenWithAuth(TEST_SESSION_1);

    expect(result).toBeNull();
    expect(mockLog).toHaveBeenCalledWith("WARN", "No revocation token found in vault", { sessionId: TEST_SESSION_1 });
  });
});