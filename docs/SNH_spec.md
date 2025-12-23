# Sovereign Neurodata Header (SNH)
Codex.Legis.Neurodata.v1 — Consent Envelope Specification

The SNH is the **session‑scoped consent envelope** that governs how a nervous‑system signal may be sensed, aggregated, retained, and revoked.  
It is the only legal basis for EEG sensing in the Neurodata Sovereign Stack.

---

## 1. Purpose

The SNH:

- Defines the **scope** of sensing  
- Defines the **granularity** of allowed data  
- Defines **retention** and **sharing** rules  
- Embeds the **revocation token hash**  
- Produces a **digest** that binds all aggregates for the session  

No EEG sensing may begin without a valid SNH.

---

## 2. SNH Fields

```json
{
  "snh_version": "1.0.0",
  "session_id": "sess-xxxx",
  "scope": ["local_vitality", "group_aggregate"],
  "granularity": "vitality_only",
  "retention_mode": "bounded",
  "sharing_level": "registry_aggregate",
  "revocation_token_hash": "sha256(...)",
  "issued_at_utc": "2025-12-23T07:22:00Z"
}

snh_digest = sha256(canonical_json(SNH))
---

# 🜁 **2. `docs/Vitality_Packet_Spec.md`**  
### *Canonical vitality packet schema*

```markdown
# Vitality Packet Specification
FPT.EEG.Vitality — Aggregate Window Format

A vitality packet is the **only EEG‑derived artifact** allowed to leave a device.  
It contains no raw samples, no waveforms, and no biometric identifiers.

---

## 1. Purpose

Vitality packets:

- summarize 8‑second EEG windows  
- provide bounded vitality + band power metrics  
- feed the Ił7 kernel  
- are hashed and logged to the Soliton Registry  

---

## 2. Packet Schema

```json
{
  "packet_version": "1.0.0",
  "session_id": "sess-xxxx",
  "group_id": "grp-xxxx",
  "time_window": {
    "start_utc": "...",
    "end_utc": "...",
    "window_seconds": 8.0
  },
  "metrics": {
    "vitality_mean": 0.66,
    "vitality_std": 0.04,
    "epsilon_d_mean": 0.0289,
    "epsilon_d_std": 0.001,
    "instability_score_mean": 0.12
  },
  "bands": {
    "alpha_mean": 0.31,
    "theta_mean": 0.14,
    "high_beta_mean": 0.08,
    "gamma_mean": 0.22
  },
  "population": {
    "node_count": 5
  },
  "snh_digest": "sha256(SNH)",
  "meta": {
    "fs": 128,
    "n_channels": 5
  }
}
vitality_packet_hash = sha256(canonical_json(packet))

---

# 🜃 **3. `docs/Soliton_Registry_Protocol.md`**  
### *Full registry protocol: aggregate, revoke, gossip, invariants*

```markdown
# Soliton Registry Protocol
Distributed, sovereign witness mesh for neurodata aggregates.

---

# 1. Purpose

The Soliton Registry is a **distributed witness**, not a blockchain.  
It records:

- vitality aggregates  
- revocation events  

It enforces Codex.Legis.Neurodata.v1 and Ił7 invariants.

---

# 2. Entry Types

## 2.1 EEG_AGGREGATE

```json
{
  "entry_id": "reg-xxxx",
  "entry_type": "EEG_AGGREGATE",
  "created_at_utc": "...",
  "payload": {
    "snh_digest": "...",
    "vitality_packet_hash": "...",
    "summary": { ... },
    "flags": { "revoked": false }
  },
  "prev_hash": "...",
  "hash": "..."
}

{
  "entry_id": "rev-xxxx",
  "entry_type": "EEG_REVOCATION",
  "created_at_utc": "...",
  "payload": {
    "revocation_token_hash": "...",
    "session_ids": ["sess-xxxx"],
    "action": "stop_future_use",
    "records_affected": 3
  },
  "prev_hash": "...",
  "hash": "..."
}

---

# 🜄 **4. `docs/Il7_invariant_proof_sketch.md`**  
### *Mathematical proof sketch of Ił7 invariants*

```markdown
# Ił7 Kernel — Invariant Proof Sketch

This document provides a proof sketch (not a full formal proof) that the Ił7 automaton satisfies its required safety and liveness invariants.

---

# 1. Sovereign Baseline Invariant

**Claim:**  
If `state ≠ SENSED`, then:

\[
vitality = 1.0 \quad \land \quad \varepsilon_d = \varepsilon_{base}
\]

**Reasoning:**  
All transitions into UNSENSED, REVOKED, SEALED explicitly set:

- vitality = 1.0  
- ε_d = ε_base  

No transition out of these states modifies vitality or ε_d except START_SENSED.

Thus the invariant holds inductively.

---

# 2. Bounded Vitality Invariant

**Claim:**  
If `state = SENSED`, then:

\[
0.5 \le vitality \le 1.5
\]

**Reasoning:**  
The only transition that modifies vitality in SENSED is EEG_VITALITY(v), which clamps v to [0.5, 1.5].  
Group modulation does not modify vitality.

Thus vitality is always in range.

---

# 3. Bounded Surplus Invariant

**Claim:**  
\[
\varepsilon_d \in [\varepsilon_{base} \cdot 0.5,\ \varepsilon_{base} \cdot 1.65]
\]

**Reasoning:**  
ε_d is computed as:

- ε_base × vitality  
- optionally × group factor ≤ 1.1  

Thus:

- min = ε_base × 0.5  
- max = ε_base × 1.5 × 1.1 = ε_base × 1.65  

---

# 4. Irreversibility of Recoil

**Claim:**  
Once REVOKE(valid) occurs, EEG cannot influence ε_d for that session.

**Reasoning:**  

1. REVOKE(valid) → state = REVOKED  
2. EPSILON_MOVE → state = UNSENSED  
3. In UNSENSED, EEG_VITALITY is ignored and ε_d = ε_base  
4. START_SENSED requires a **new** session_id  

Thus the revoked session can never re‑enter SENSED.

---

# 5. No EEG Influence Outside SENSED

**Claim:**  
If `state ≠ SENSED`, EEG_VITALITY does not change ε_d.

**Reasoning:**  
EEG_VITALITY handler checks:

Thus EEG cannot influence surplus outside SENSED.

---

# 6. Liveness: Revocation Leads to Baseline

**Claim:**  
If REVOKE(valid) occurs, eventually state = UNSENSED.

**Reasoning:**  
REVOKE(valid) → REVOKED → EPSILON_MOVE → UNSENSED.  
EPSILON_MOVE is guaranteed by implementation (timer or next tick).

Thus liveness holds.

---

# 7. Liveness: No Deadlock in REVOKED/SEALED

**Claim:**  
System cannot remain indefinitely in REVOKED or SEALED.

**Reasoning:**  
Both states have mandatory ε‑moves to UNSENSED.

Thus no deadlock.

---

# Conclusion

All required invariants follow from:

- explicit transition definitions  
- clamping rules  
- ε‑moves  
- session‑scoped consent  

The Ił7 kernel is therefore a **sound and sovereign gate** for neurodata.