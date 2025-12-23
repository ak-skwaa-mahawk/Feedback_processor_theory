/*
 * Ił7 Kernel — Reference Implementation (Pure TypeScript)
 * Deterministic Mealy Automaton for Neurodata Sovereignty
 */

export type Il7State = "UNSENSED" | "SENSED" | "REVOKED" | "SEALED";

export interface KernelSnapshot {
  state: Il7State;
  vitality: number;
  epsilonD: number;
  sessionId: string | null;
  revocationTokenHash: string | null;
  lastEvent: string;
}

export class Il7Kernel {
  private epsilonBase = 0.0417;

  private snapshot: KernelSnapshot = {
    state: "UNSENSED",
    vitality: 1.0,
    epsilonD: this.epsilonBase,
    sessionId: null,
    revocationTokenHash: null,
    lastEvent: "INIT"
  };

  get state() { return this.snapshot; }

  private clamp(v: number) {
    return Math.max(0.5, Math.min(1.5, v));
  }

  startSensed(sessionId: string, tokenHash: string) {
    if (!["UNSENSED", "REVOKED", "SEALED"].includes(this.snapshot.state)) return;

    this.snapshot = {
      state: "SENSED",
      vitality: 1.0,
      epsilonD: this.epsilonBase,
      sessionId,
      revocationTokenHash: tokenHash,
      lastEvent: "START_SENSED"
    };
  }

  eegVitality(v: number) {
    if (this.snapshot.state !== "SENSED") {
      this.snapshot.lastEvent = "EEG_IGNORED";
      this.snapshot.epsilonD = this.epsilonBase;
      return;
    }

    const vitality = this.clamp(v);
    this.snapshot.vitality = vitality;
    this.snapshot.epsilonD = this.epsilonBase * vitality;
    this.snapshot.lastEvent = "EEG_VITALITY";
  }

  groupModulation(groupVitality: number, groupCoherence: number) {
    if (this.snapshot.state !== "SENSED") return;

    let factor = 1.0;
    if (groupVitality > 1.0 && groupCoherence > 0.7) {
      factor = 1 + Math.min(0.1, (groupVitality - 1.0) * groupCoherence);
    }

    this.snapshot.epsilonD = Math.min(
      this.epsilonBase * this.snapshot.vitality * factor,
      this.epsilonBase * 1.5 * 1.1
    );

    this.snapshot.lastEvent = "GROUP_MODULATION";
  }

  revoke(tokenHash: string) {
    if (this.snapshot.state === "SENSED" &&
        tokenHash === this.snapshot.revocationTokenHash) {

      this.snapshot = {
        state: "REVOKED",
        vitality: 1.0,
        epsilonD: this.epsilonBase,
        sessionId: null,
        revocationTokenHash: null,
        lastEvent: "REVOKE_ACCEPTED"
      };
      return;
    }

    this.snapshot.lastEvent = "REVOKE_INVALID";
  }

  endSessionNormal() {
    if (this.snapshot.state !== "SENSED") return;

    this.snapshot = {
      state: "SEALED",
      vitality: 1.0,
      epsilonD: this.epsilonBase,
      sessionId: null,
      revocationTokenHash: null,
      lastEvent: "END_NORMAL"
    };
  }

  epsilonMove() {
    if (!["REVOKED", "SEALED"].includes(this.snapshot.state)) return;

    this.snapshot = {
      state: "UNSENSED",
      vitality: 1.0,
      epsilonD: this.epsilonBase,
      sessionId: null,
      revocationTokenHash: null,
      lastEvent: "EPSILON_MOVE"
    };
  }
}