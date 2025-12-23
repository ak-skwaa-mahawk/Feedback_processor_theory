/*
 * Unit Tests: Token Vault + Logger Integration
 * Verifies sovereign witnessing of vault acts
 */

import { generateAndStoreToken, getTokenWithAuth, deleteToken, exportTokenReceipt } from "../services/tokenVault";
import { logger } from "../services/logger";
import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";

// Mock SecureStore
jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

// Mock LocalAuthentication (no biometrics in test)
jest.mock("expo-local-authentication", () => ({
  hasHardwareAsync: jest.fn().mockResolvedValue(false),
  isEnrolledAsync: jest.fn().mockResolvedValue(false),
}));

// Spy on logger methods
const mockAppend = jest.spyOn(logger as any, "appendEntry");
const mockLog = jest.fn();
Object.defineProperty(logger, "log", { value: mockLog, writable: true });

const TEST_SESSION = "test-session-1234";

beforeEach(() => {
  jest.clearAllMocks();
  mockAppend.mockImplementation(() => Promise.resolve());
});

describe("Token Vault + Logger Integration", () => {
  test("generateAndStoreToken logs generation at INFO and SOVEREIGN", async () => {
    (SecureStore.setItemAsync as jest.Mock).mockResolvedValueOnce(undefined);

    await generateAndStoreToken(TEST_SESSION);

    expect(mockLog).toHaveBeenCalledWith("INFO", "Storing new revocation token", expect.objectContaining({
      sessionId: TEST_SESSION,
      tokenPreview: expect.stringMatching(/R7-[A-Z0-9]{2}\*\*\*\*/),
    }));

    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token generated and vaulted", {
      sessionId: TEST_SESSION,
    });
  });

  test("generateAndStoreToken logs ERROR on storage failure", async () => {
    (SecureStore.setItemAsync as jest.Mock).mockRejectedValueOnce(new Error("disk full"));

    await expect(generateAndStoreToken(TEST_SESSION)).rejects.toThrow("STORAGE_FAILURE");

    expect(mockLog).toHaveBeenCalledWith("ERROR", "Failed to generate/store revocation token", expect.objectContaining({
      sessionId: TEST_SESSION,
      error: "disk full",
    }));
  });

  test("getTokenWithAuth logs access flow and redacts token", async () => {
    const fakeToken = "R7-ABCDEF12";
    const vaulted = {
      sessionId: TEST_SESSION,
      token: fakeToken,
      tokenHash: "hash",
      createdAt: new Date().toISOString(),
    };

    (SecureStore.getItemAsync as jest.Mock).mockResolvedValueOnce(JSON.stringify(vaulted));

    const result = await getTokenWithAuth(TEST_SESSION);

    expect(result?.token).toBe(fakeToken);

    expect(mockLog).toHaveBeenCalledWith("INFO", "Requesting revocation token from vault", { sessionId: TEST_SESSION });

    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token accessed successfully", {
      sessionId: TEST_SESSION,
      tokenPreview: "R7-AB****",
    });
  });

  test("getTokenWithAuth logs WARN when token missing", async () => {
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValueOnce(null);

    const result = await getTokenWithAuth(TEST_SESSION);

    expect(result).toBeNull();
    expect(mockLog).toHaveBeenCalledWith("WARN", "No revocation token found in vault", { sessionId: TEST_SESSION });
  });

  test("exportTokenReceipt logs export at SOVEREIGN", async () => {
    const vaulted = {
      sessionId: TEST_SESSION,
      token: "R7-XYZ12345",
      tokenHash: "hash",
      createdAt: new Date().toISOString(),
    };

    (SecureStore.getItemAsync as jest.Mock)
      .mockResolvedValueOnce(JSON.stringify(vaulted)) // for getTokenWithAuth
      .mockResolvedValueOnce(JSON.stringify(vaulted)); // fallback

    const receipt = await exportTokenReceipt(TEST_SESSION);

    expect(receipt?.exportedAt).toBeDefined();
    expect(mockLog).toHaveBeenCalledWith("INFO", "Exporting revocation receipt", { sessionId: TEST_SESSION });
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation receipt exported", { sessionId: TEST_SESSION });
  });

  test("deleteToken logs deletion at SOVEREIGN", async () => {
    (SecureStore.deleteItemAsync as jest.Mock).mockResolvedValueOnce(undefined);

    await deleteToken(TEST_SESSION);

    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token securely deleted from vault", {
      sessionId: TEST_SESSION,
    });
  });

  test("deleteToken logs ERROR on failure", async () => {
    (SecureStore.deleteItemAsync as jest.Mock).mockRejectedValueOnce(new Error("access denied"));

    await expect(deleteToken(TEST_SESSION)).rejects.toThrow("DELETE_FAILED");

    expect(mockLog).toHaveBeenCalledWith("ERROR", "Failed to delete revocation token", {
      sessionId: TEST_SESSION,
      error: "access denied",
    });
  });

  test("sanitizeContext redacts tokens and blocks neurodata", () => {
    const input = {
      token: "R7-FULLTOKEN123",
      eeg_samples: [1, 2, 3],
      safe: "hello",
    };

    const loggerAny = logger as any;
    const sanitized = loggerAny.sanitizeContext(input);

    expect(sanitized.token).toMatch(/R7-....\*\*\*\*....$/);
    expect(sanitized.eeg_samples).toBe("[REDACTED_NEURODATA]");
    expect(sanitized.safe).toBe("hello");
  });
});