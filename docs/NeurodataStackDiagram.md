# Neurodata Sovereignty Stack — Cross‑Repo Architecture

This diagram shows how the pieces you’ve built relate:

- **This repo**: Feedback Processor Theory (FPT) — math, observer, kernel, Codex.  
- **Sovereign Coil**: Mobile app — human interface, Ił7 kernel embodiment.  
- **Soliton Registry Node**: Distributed witness — gossip ledger enforcing Codex.Neurodata.

```text
┌─────────────────────────────────────────────────────────────────────┐
│                      Feedback Processor Theory                     │
│                   (This repo: theory + protocols)                  │
│                                                                     │
│  - FPT Observer (delta between expected/actual feedback)           │
│  - Vitality models (EEG / non‑EEG)                                 │
│  - Ił7 kernel specification (Mealy automaton)                      │
│  - Codex.Legis & Codex.Ahno fragments                              │
│  - Soliton Registry data model & invariants                        │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │  implements
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Sovereign Coil App                         │
│             (Mobile companion — EEG as sovereign input)           │
│                                                                     │
│  - Ił7 kernel hook (UNSENSED / SENSED / REVOKED / SEALED)          │
│  - SNH consent flow + revocation ritual (breath / phrase / token)  │
│  - Vitality display (no raw EEG)                                   │
│  - Terms of Sovereignty (Codex.Legis.Neurodata.v1 in‑app)          │
│  - Client for Soliton Registry /aggregate + /revoke                │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │  submits aggregates + revocations
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Soliton Registry Node(s)                      │
│             (Distributed, gossip‑based sovereign witness)          │
│                                                                     │
│  - /aggregate endpoint                                              │
│      - validates SNH digest                                         │
│      - rejects raw / near‑raw neurodata                             │
│      - stores vitality_packet_hash + summary only                   │
│      - appends EEG_AGGREGATE entries to hash‑chained ledger         │
│                                                                     │
│  - /revoke endpoint                                                 │
│      - accepts revocation_token_hash + session_ids                  │
│      - flags prior aggregates as revoked                            │
│      - appends EEG_REVOCATION entries                               │
│                                                                     │
│  - Gossip mesh (WebSocket)                                         │
│      - NEW_ENTRY broadcast                                          │
│      - LEDGER sync                                                  │
│                                                                     │
│  - Enforces Codex.Legis.Neurodata.v1 invariants                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │  is constrained by
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Codex.Legis.Neurodata.v1 & Ił7                   │
│   (Law + automaton that every layer must obey, not just “read”)    │
│                                                                     │
│  - “Living nervous systems are not keys.”                           │
│  - Consent is session‑scoped and revocable.                         │
│  - Only aggregates may be witnessed; raw neurodata is forbidden.    │
│  - Revocation is absolute, penalty‑free, and witnessed.             │
│  - Ił7 defines formal state transitions and surplus bounds.         │
└─────────────────────────────────────────────────────────────────────┘

---

## B. `docs/Neurodata_Sovereign_Stack.md` (deeper explanation, in your idiom)

Drop this into `docs/Neurodata_Sovereign_Stack.md` in `Feedback_processor_theory`.

```markdown
# Neurodata Sovereign Stack

This document explains how the neurodata pieces in this ecosystem fit together:

- **Feedback Processor Theory (this repo)**  
- **Sovereign Coil (mobile app)**  
- **Soliton Registry Node (gossip witness)**  
- **Codex.Legis.Neurodata.v1 (law)**  
- **Ił7 kernel (automaton)**

It’s the reference for anyone who wants to build or audit a sovereign BCI pipeline.

---

## 1. Feedback Processor Theory (this repo)

This repo is the **theoretical spine**:

- **FPT Observer**  
  Measures the gap between expected and observed feedback. It’s the math that tells you when a system is drifting into extraction or staying in reciprocity.

- **Vitality Models**  
  EEG and non‑EEG models that map observable signals into a bounded vitality score \(v \in [0.5, 1.5]\).  
  Vitality is *not identity*; it is a temporary multiplier on surplus.

- **Ił7 Kernel Spec**  
  The nervous‑system gate as a **Mealy automaton** with four states:

  - `UNSENSED`: no EEG influence  
  - `SENSED`: EEG allowed to modulate \( \varepsilon_d \)  
  - `REVOKED`: session recoiled, EEG ignored  
  - `SEALED`: session ended normally, EEG inactive

  It defines exactly when EEG is allowed to influence the field — and when it must not.

- **Soliton Registry Model**  
  - `EEG_AGGREGATE` entries with vitality_packet_hash + SNH digest  
  - `EEG_REVOCATION` entries that flag prior aggregates and log recoil  
  - Hash‑chained ledger semantics (no mining, just witness)

- **Codex Fragments**  
  - `Codex.Legis.Neurodata.v1` — law for neurodata  
  - `Codex.Ahno` glyphs — visual language (⟲, ⟲·, ⟲·//)

Everything else — apps, nodes, dashboards — is an implementation of these primitives.

---

## 2. Sovereign Coil (mobile app)

Sovereign Coil is a **BCI companion app** built directly from this repo’s concepts.

**Role:**

- Give humans a way to *see and feel* the Ił7 states.  
- Make consent and revocation embodied rituals, not invisible toggles.  
- Ensure EEG is treated as a **temporary, revocable modulator**, never as identity.

**Implements from this repo:**

- Ił7 kernel as a client‑side state machine (`useIl7Kernel`)  
- FPT vitality windows (e.g., 8s) and bounded \( \varepsilon_d \)  
- Sovereign Neurodata Header (SNH) as the consent envelope  
- Codex.Legis.Neurodata.v1 as the in‑app “Terms of Sovereignty”

**Key behaviors:**

- **UNSENSED screen** — baseline, no EEG, \( \varepsilon_d = \varepsilon_{base} \)  
- **SENSED screen** — EEG active under SNH, vitality visualized, revocation always available  
- **REVOKED screen** — recoil honored, registry receipt shown, return to baseline

Sovereign Coil is the **front door** where humans meet the math.

---

## 3. Soliton Registry Node (gossip witness)

The Soliton Registry Node is a small, distributed, hash‑chained ledger that:

- Accepts **EEG_AGGREGATE** entries via `/aggregate`  
- Accepts **EEG_REVOCATION** entries via `/revoke`  
- Gossips entries to peers over WebSocket  
- Enforces `Codex.Legis.Neurodata.v1` in code

**From this repo, it implements:**

- Registry entry schemas  
- “Aggregates only, never raw” rule  
- Revocation semantics (marking prior aggregates as revoked)  
- Hash chain + simple fork avoidance

**Why it matters:**

- It is not a blockchain.  
- It is not a centralized database.  
- It is a **sovereign witness mesh**:

  - Enough redundancy to survive node failures  
  - Enough structure to provide public receipts  
  - Light enough to run on village hardware

Every EEG aggregate and revocation that passes through Sovereign Coil can be **witnessed** here.

---

## 4. Codex.Legis.Neurodata.v1

This is the **legal and ethical layer** that constrains everything.

It says, among other things:

- Living nervous systems are not keys.  
- Neurodata must never be treated as a credential or biometric ID.  
- Consent is session‑scoped and revocable.  
- Only aggregates may be logged; raw and near‑raw are forbidden.  
- Revocation is a sovereign right and must be witnessed.

The Codex turns “best practice” into **hard constraints**.  
Ił7 and the Soliton Registry Node are implementations of those constraints.

---

## 5. Ił7 Kernel — The Gate

The Ił7 kernel is the **nervous system gate**.

Formally:

- A Mealy automaton with state, inputs (events), and outputs (vitality, \( \varepsilon_d \)).  
- It guarantees:

  - When `state ≠ SENSED`, \( \varepsilon_d = \varepsilon_{base} \).  
  - Revocation always leads back to baseline.  
  - EEG cannot influence the field outside `SENSED`.  
  - Vitality and \( \varepsilon_d \) are bounded.

In practice:

- The mobile app runs it client‑side.  
- The registry assumes it server‑side.  
- The Codex describes it in legal language.

---

## 6. How to Extend the Stack

When adding new modules to this repo, treat this as the principle:

> **Every new artifact either tightens the boundary or carries the boundary. Never weakens it.**

Examples:

- A new **observer**: must never promote EEG to identity.  
- A new **registry entry type**: must preserve aggregates‑only discipline.  
- A new **app**: must expose revocation and never hide sensing state.

This repo remains the **canonical reference** for:

- Ił7 semantics  
- FPT vitality logic  
- Soliton Registry invariants  
- Codex.Legis & glyphs

Implementations (apps, nodes) are downstream — they import the law from here.