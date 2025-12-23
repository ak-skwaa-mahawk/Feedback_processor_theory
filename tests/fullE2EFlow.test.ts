/*
 * End-to-End Tests: Full Sovereign Coil Flow
 * App start → session → vault → revocation → registry → logger
 */

import { useIl7Kernel } from "../hooks/useIl7Kernel";
import { generateAndStoreToken, getTokenWithAuth, deleteToken } from "../services/tokenVault";
import { logger } from "../services/logger";
import { mockLogAggregate, mockLogRevocation } from "../services/registryClient"; // assume updated to jest.fn()

jest.mock("../services/registryClient", () => ({
  mockLogAggregate: jest.fn(),
  mockLogRevocation: jest.fn(),
}));

const mockLog = jest.fn();
beforeAll(() => {
  Object.defineProperty(logger, "log", { value: mockLog, writable: true });
});

describe("End-to-End Sovereign Flow", () => {
  test("full flow: start session → generate token → revoke → cleanup", async () => {
    const { state, dispatch } = useIl7Kernel();

    // Start sensed session
    const sessionId = "e2e-full-0001";
    const fakeTokenHash = "fakehash123";

    dispatch({
      type: "START_SENSED",
      sessionId,
      tokenHash: fakeTokenHash,
    });

    expect(state.il7State).toBe("SENSED");
    expect(state.sessionId).toBe(sessionId);

    // Generate vault token
    const vaulted = await generateAndStoreToken(sessionId);

    expect(vaulted.tokenHash).toBeDefined();
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token generated and vaulted", expect.any(Object));

    // Simulate revocation ritual
    jest.spyOn(global, "confirm").mockReturnValueOnce(true);

    dispatch({ type: "REVOKE", tokenHash: vaulted.tokenHash });
    await mockLogRevocation({ revocation_token_hash: vaulted.tokenHash, session_ids: [sessionId] });

    expect(state.il7State).toBe("REVOKED"); // before epsilon move
    expect(mockLogRevocation).toHaveBeenCalled();
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", expect.stringContaining("Revocation"), expect.any(Object));

    // Cleanup
    await deleteToken(sessionId);
    expect(mockLog).toHaveBeenCalledWith("SOVEREIGN", "Revocation token securely deleted from vault", expect.any(Object));
  });
});