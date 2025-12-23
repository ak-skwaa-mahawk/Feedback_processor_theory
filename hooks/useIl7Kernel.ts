import { useReducer, useEffect } from "react";
import { EPSILON_BASE, VITALITY_MIN, VITALITY_MAX, EPSILON_MAX_BOOST } from "../types";
import type { Il7State, KernelState } from "../types";

type Action =
  | { type: "START_SENSED"; sessionId: string; tokenHash: string }
  | { type: "EEG_VITALITY"; vitality: number }
  | { type: "GROUP_MODULATION"; groupVitality: number; groupCoherence: number }
  | { type: "REVOKE"; tokenHash: string }
  | { type: "END_NORMAL" }
  | { type: "EPSILON_MOVE" }; // auto cleanup

const initialState: KernelState = {
  il7State: "UNSENSED",
  vitality: 1.0,
  epsilonD: EPSILON_BASE,
  sessionId: null,
  revocationTokenHash: null,
  lastEvent: "INIT",
};

function kernelReducer(state: KernelState, action: Action): KernelState {
  switch (action.type) {
    case "START_SENSED":
      if (!["UNSENSED", "REVOKED", "SEALED"].includes(state.il7State)) {
        return state; // invalid transition
      }
      return {
        ...state,
        il7State: "SENSED",
        sessionId: action.sessionId,
        revocationTokenHash: action.tokenHash,
        vitality: 1.0,
        epsilonD: EPSILON_BASE,
        lastEvent: "START_SENSED",
      };

    case "EEG_VITALITY":
      const clamped = Math.max(VITALITY_MIN, Math.min(VITALITY_MAX, action.vitality));
      if (state.il7State === "SENSED") {
        return {
          ...state,
          vitality: clamped,
          epsilonD: EPSILON_BASE * clamped,
          lastEvent: "EEG_VITALITY",
        };
      }
      // outside SENSED: ignore
      return { ...state, lastEvent: "EEG_IGNORED" };

    case "GROUP_MODULATION":
      if (state.il7State !== "SENSED") return state;
      let factor = 1.0;
      if (action.groupVitality > 1.0 && action.groupCoherence > 0.7) {
        factor = 1 + Math.min(0.1, (action.groupVitality - 1.0) * action.groupCoherence);
      }
      return {
        ...state,
        epsilonD: Math.min(EPSILON_BASE * state.vitality * factor, EPSILON_BASE * VITALITY_MAX * EPSILON_MAX_BOOST),
        lastEvent: "GROUP_MODULATION",
      };

    case "REVOKE":
      if (state.il7State === "SENSED" && action.tokenHash === state.revocationTokenHash) {
        return {
          ...initialState,
          il7State: "REVOKED",
          lastEvent: "REVOKE_ACCEPTED",
        };
      }
      return { ...state, lastEvent: "REVOKE_INVALID" };

    case "END_NORMAL":
      if (state.il7State === "SENSED") {
        return {
          ...initialState,
          il7State: "SEALED",
          lastEvent: "END_NORMAL",
        };
      }
      return state;

    case "EPSILON_MOVE":
      if (["REVOKED", "SEALED"].includes(state.il7State)) {
        return { ...initialState, il7State: "UNSENSED", lastEvent: "EPSILON_MOVE" };
      }
      return state;

    default:
      return state;
  }
}

export function useIl7Kernel() {
  const [state, dispatch] = useReducer(kernelReducer, initialState);

  // Auto-cleanup REVOKED/SEALED → UNSENSED after brief display
  useEffect(() => {
    if (["REVOKED", "SEALED"].includes(state.il7State)) {
      const timer = setTimeout(() => dispatch({ type: "EPSILON_MOVE" }), 8000);
      return () => clearTimeout(timer);
    }
  }, [state.il7State]);

  return { state, dispatch };
}