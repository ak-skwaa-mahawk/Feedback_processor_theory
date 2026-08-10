export type Il7State = "UNSENSED" | "SENSED" | "REVOKED" | "SEALED";

export interface KernelState {
  il7State: Il7State;
  vitality: number;
  epsilonD: number;
  sessionId: string | null;
  revocationTokenHash: string | null;
  lastEvent: string;
}

export const EPSILON_BASE = 0.0417;
export const VITALITY_MIN = 0.5;
export const VITALITY_MAX = 1.5;
export const EPSILON_MAX_BOOST = 1.1; // group modulation cap
Added new TypeScript types, SessionData and SavedSession, to define the structure for storing and managing user sessions in local storage.
Add the Survey, SurveyQuestion, and QuestionType types to support the new AI-powered survey generation feature.