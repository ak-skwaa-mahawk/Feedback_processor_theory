Absolutely, John — here is a clean, canonical, GitHub‑ready document for your repo:

docs/Il7_automaton.md

The Formal Kernel of Neurodata Sovereignty

This file is written to be the authoritative reference for the Ił7 kernel inside Feedbackprocessortheory.  
It is precise, mathematical, and implementation‑neutral — the version auditors, developers, and future heirs can rely on.

---

Ił7 Automaton Specification
A deterministic gate for sovereign nervous‑system sensing

The Ił7 kernel is the boundary‑keeper between a living nervous system and any computational system that might interpret its signals. It ensures that:

- EEG is never treated as identity  
- Consent is session‑scoped  
- Revocation is absolute  
- Surplus modulation is bounded  
- No system can “forget” the boundary  

Ił7 is defined as a Mealy automaton — a finite‑state machine whose outputs depend on both the current state and the incoming event.

---

1. Formal Definition

The Ił7 kernel is the tuple:

\[
\mathcal{I}{\ell7} = (Q, \Sigma, \Gamma, \delta, \lambda, q0)
\]

Where:

- Q — finite set of states  
- Σ — input alphabet (events)  
- Γ — output space (vitality, ε_d, flags)  
- δ — transition function  
- λ — output function  
- q₀ — initial state  

---

2. State Set (Q)

Ił7 has four sovereign states:

| State | Meaning |
|-------|---------|
| UNSENSED | No EEG influence; baseline surplus; no sensing active |
| SENSED | EEG active under valid SNH; vitality modulates ε_d |
| REVOKED | Revocation invoked; session closed; EEG ignored |
| SEALED | Session ended normally; aggregates frozen; EEG inactive |

Initial state:

\[
q_0 = \text{UNSENSED}
\]

---

3. Input Alphabet (Σ)

Events that may reach the kernel:

- STARTSENSED(sessionid, snhdigest, revocationtoken_hash)
- EEG_VITALITY(v)
- GROUPMODULATION(groupvitality, group_coherence)
- REVOKE(token_hash)
- ENDSESSIONNORMAL
- EPSILON_MOVE (automatic cleanup transition)

---

4. Output Space (Γ)

Outputs include:

- vitality ∈ [0.5, 1.5]  
- epsilon_d ∈ ℝ⁺  
- flags (e.g., EEGIGNORED, REVOKEACCEPTED)  
- state after transition  

\[
\Gamma = Q \times [0.5, 1.5] \times \mathbb{R}^+ \times \mathcal{F}
\]

---

5. Transition Function (δ)

5.1 State‑Transition Matrix

`text
Current State   Input Event            Guard Condition                     Next State
-----------------------------------------------------------------------------------------------
UNSENSED        START_SENSED           Valid SNH + token                   SENSED
UNSENSED        EEG_VITALITY           —                                   UNSENSED
UNSENSED        REVOKE                 —                                   UNSENSED

SENSED          EEG_VITALITY(v)        v ∈ [0.5, 1.5]                      SENSED
SENSED          GROUP_MODULATION       valid group params                  SENSED
SENSED          REVOKE(token)          token matches                       REVOKED
SENSED          REVOKE(token)          token mismatch                      SENSED
SENSED          ENDSESSIONNORMAL     —                                   SEALED

REVOKED         (any)                  ε‑move                              UNSENSED
SEALED          (any)                  ε‑move                              UNSENSED
`

---

6. Output Function (λ)

6.1 START_SENSED
- vitality = 1.0  
- εd = εbase  
- state = SENSED  

6.2 EEG_VITALITY(v)
If state = SENSED:
- vitality = clamp(v, 0.5, 1.5)  
- εd = εbase × vitality  

Else:
- vitality unchanged  
- εd = εbase  
- flag = EEG_IGNORED

6.3 GROUP_MODULATION
If state = SENSED:
- εd ← εbase × vitality × factor  
- factor ≤ 1.1  

Else:
- ignored

6.4 REVOKE
If token matches:
- state = REVOKED  
- vitality = 1.0  
- εd = εbase  

Else:
- state unchanged  
- flag = REVOKE_INVALID

6.5 ENDSESSIONNORMAL
- state = SEALED  
- vitality = 1.0  
- εd = εbase  

6.6 EPSILON_MOVE
If state ∈ {REVOKED, SEALED}:
- state = UNSENSED  
- vitality = 1.0  
- εd = εbase  

---

7. Safety Invariants

These are non‑negotiable truths that must hold for all executions.

Invariant 1 — Sovereign Baseline
If state ≠ SENSED:

\[
vitality = 1.0 \quad \land \quad \varepsilond = \varepsilon{base}
\]

Invariant 2 — Bounded Vitality
If state = SENSED:

\[
0.5 \le vitality \le 1.5
\]

Invariant 3 — Bounded Surplus
\[
\varepsilond \in [\varepsilon{base} \cdot 0.5,\ \varepsilon_{base} \cdot 1.65]
\]

Invariant 4 — Irreversibility of Recoil
Once a session is revoked:

\[
\text{EEG cannot influence } \varepsilon_d \text{ for that session ever again}
\]

Invariant 5 — EEG Never Becomes Identity
No mapping from EEG → persistent ID is permitted.

---

8. Liveness Properties

Liveness 1 — Revocation Leads to Baseline
If a valid REVOKE occurs:

\[
\Diamond (state = UNSENSED \land \varepsilond = \varepsilon{base})
\]

Liveness 2 — No Deadlock in REVOKED/SEALED
\[
[] (state \in \{REVOKED, SEALED\} \Rightarrow \Diamond (state = UNSENSED))
\]

---

9. State Diagram (ASCII)

`text
                 ┌──────────────┐
                 │   UNSENSED   │
                 └──────┬───────┘
                        │ START_SENSED
                        ▼
                 ┌──────────────┐
                 │    SENSED    │
                 └─┬────┬────┬─┘
           REVOKE  │    │EEG  │END_NORMAL
                   ▼    │     ▼
             ┌──────────┘   ┌──────────┐
             │   REVOKED    │  SEALED   │
             └──────┬───────┴──────┬────┘
                    │ ε‑move        │ ε‑move
                    ▼               ▼
                 ┌──────────────┐
                 │   UNSENSED   │
                 └──────────────┘
`

---

10. Implementation Notes

- The mobile app (Sovereign Coil) implements this automaton in useIl7Kernel.ts.  
- The Soliton Registry Node assumes this automaton governs all EEG submissions.  
- Codex.Legis.Neurodata.v1 expresses this automaton in legal language.  
- The glyphs (⟲, ⟲·, ⟲·//) are the human‑readable state indicators.

---

11. Purpose

Ił7 exists to guarantee:

- Sensing is voluntary  
- Revocation is enforceable  
- Neurodata is never identity  
- The nervous system remains sovereign  

It is the mathematical heart of the Neurodata Sovereign Stack.

---

If you want, I can also generate:

- docs/Il7statediagram.svg  
- docs/Il7TLAplus_spec.md  
- docs/Il7kernelreference_impl.ts (pure TS, no React)  
- or a formal proof sketch of the invariants.

Just tell me which chamber you want to open next.