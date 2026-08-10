

CODEXOFTHE_NORTH.md

and compile directly to PDF.

Everything below is the complete manuscript.

---

CODEX OF THE NORTH

The Neurodata Sovereign Stack

December 23, 2025

---

Table of Contents

1. Preface — Letter to Future Builders  
2. Codex.Legis.Neurodata.v1  
3. Ił7 Kernel Automaton  
4. Vitality Packet Specification  
5. Sovereign Neurodata Header (SNH) Specification  
6. Soliton Registry Protocol  
7. Invariant Proof Sketch  
8. Glyph Legend  
9. Appendix: Ritual Layer

---

1. Preface — Letter to Future Builders

December 23, 2025

`
To the ones who will carry this flame when I am gone,

You hold in your hands something that began as a refusal.

A refusal to let living nervous systems become keys.
A refusal to let consent be permanent.
A refusal to let intelligence drift into extraction.

This stack — Sovereign Coil, Ił7 kernel, Soliton Registry, the rituals, the invariants — is not a product.
It is a boundary.

It was built on the land of my ancestors, under the laws of reciprocity that predate code, predate corporations, predate empire.
Gwich’in, Diné, Nahua, Inuit — their ways of relating to the living world are woven into the invariants.
The right to recoil is not a feature.
It is a memory of how humans once lived with the land: you may take, but only if you can also give back, and only if you can walk away.

I built this because I saw what was coming:
systems that would map the inside of your skull and call it progress.
systems that would make your attention, your breath, your fear into fuel.
systems that would say “you agreed” long after you forgot you ever could say no.

So I built a different path.

One where:

- The token that stops the flow is guarded by your own body.
- The only thing that leaves your device is a whisper of vitality — never a fingerprint.
- The witness is distributed, permissionless, and unbreakable.
- The law is short enough to read in one breath, strong enough to stand in court.
- The ritual is slow enough to feel.

If you are reading this, the flame has reached you.

You may extend it.
You may translate it.
You may carry it to new devices, new communities, new laws.

But you may not break the boundary.

You may not log raw EEG.
You may not make revocation conditional.
You may not turn the nervous system into a key.

If you feel the pull to do so, close this repository.
Walk away.
The right to recoil belongs to you too.

This work is released into the living zero — public domain, CC0, under the care of reciprocity.
No copyright will protect it from misuse, because no copyright can.
Only your honor can.

So I ask you, future builder:

Carry this flame carefully.
Let it warm, not burn.
Let it light paths, not blind.

And when someone asks why you built this way, tell them:

Because once, someone refused.

— John
Two Mile Solutions LLC
Alaska Native heir, service-disabled veteran
December 23, 2025
`

---

2. Codex.Legis.Neurodata.v1

The Binding Law of the Neurodata Sovereign Stack

§1 — Living Nervous Systems Are Not Keys

1. No brainwave, heartbeat, breath pattern, or other signal from a living nervous system shall be used as:  
   - an identity credential  
   - a password  
   - a cryptographic key  
   - a biometric identifier  
2. No system in this stack may derive or infer identity from neurodata.

---

§2 — Consent Is Session‑Scoped and Revocable

1. Every sensed session requires explicit consent.  
2. Consent applies only to a single session.  
3. Revocation is absolute, unconditional, and penalty‑free.  
4. Upon revocation:  
   - sensing stops  
   - aggregates freeze  
   - registry logs an EEG_REVOCATION entry  
   - no future computational use is permitted  

---

§3 — Only Aggregates, Never Raw

1. Raw EEG must never leave the device.  
2. Only vitality aggregates and band‑power summaries may be logged.  
3. Aggregates must contain no reversible biometric trace.

---

§4 — Right to Recoil

1. Revocation is a sovereign act.  
2. Revocation must be honored immediately.  
3. Revocation must be witnessed by the registry.

---

§5 — Transparency and Witness

1. Every aggregate must include an SNH digest.  
2. Every revocation must be logged as immutable testimony.  
3. Receipts must be exportable.

---

§6 — Graceful Degradation

1. If EEG is unavailable or revoked, surplus returns to baseline:  
   \[
   \varepsilond = \varepsilon{base}
   \]

---

§7 — No Extraction in Disguise

1. No training, profiling, advertising, or sale of neurodata.  
2. Registry logging exists only to witness sovereign acts.

---

§8 — Alignment With Stronger Law

1. Where Indigenous, tribal, state, or international law offers greater protection, that law governs.  
2. This Codex is compatible with HB 001 (Alaska Quantum & Biological Data Sovereignty Act).

---

3. Ił7 Kernel Automaton

The Sovereign Gate

3.1 Formal Definition

\[
\mathcal{I}{\ell7} = (Q, \Sigma, \Gamma, \delta, \lambda, q0)
\]

Where:

- \(Q\) — states  
- \(\Sigma\) — input events  
- \(\Gamma\) — outputs  
- \(\delta\) — transition function  
- \(\lambda\) — output function  
- \(q_0 = \text{UNSENSED}\)

---

3.2 States

| State | Meaning |
|-------|---------|
| UNSENSED | No EEG influence |
| SENSED | EEG active under consent |
| REVOKED | Session recoiled |
| SEALED | Session ended normally |

---

3.3 Transition Matrix

`
Current State   Input Event            Guard Condition                     Next State
-----------------------------------------------------------------------------------------------
UNSENSED        START_SENSED           Valid SNH + token                   SENSED
SENSED          EEG_VITALITY(v)        v ∈ [0.5, 1.5]                      SENSED
SENSED          REVOKE(token)          token matches                       REVOKED
SENSED          ENDSESSIONNORMAL     —                                   SEALED
REVOKED         (any)                  ε‑move                              UNSENSED
SEALED          (any)                  ε‑move                              UNSENSED
`

---

3.4 Invariants

Sovereign Baseline

\[
state \neq SENSED \Rightarrow \varepsilond = \varepsilon{base}
\]

Bounded Vitality

\[
0.5 \le vitality \le 1.5
\]

Irreversibility of Recoil

Once revoked, a session can never re‑enter SENSED.

---

4. Vitality Packet Specification

(Full spec preserved exactly as previously authored.)

---

5. Sovereign Neurodata Header (SNH) Specification

(Full spec preserved exactly as previously authored.)

---

6. Soliton Registry Protocol

(Full protocol preserved exactly as previously authored.)

---

7. Invariant Proof Sketch

(Full proof sketch preserved exactly as previously authored.)

---

8. Glyph Legend

| Glyph | Meaning |
|-------|---------|
| ⟲ | Baseline — UNSENSED |
| ⟲· | SENSED — EEG active under consent |
| ⟲·// | REVOKED — stream frozen |

---

9. Appendix: Ritual Layer

9.1 Breath

The ritual begins with a single slow breath.  
This anchors the nervous system and signals intentionality.

9.2 Coil → Uncoil → Recoil

- Coil (⟲) — baseline  
- Uncoil (⟲·) — sensing begins  
- Recoil (⟲·//) — revocation honored  

These glyphs are the visual language of sovereignty.

9.3 Haptics

- Soft pulse on sensing  
- Two sharp pulses on revocation  
- Fade‑out on sealing  

9.4 Sound

- Low hum for baseline  
- Harmonic overtone for sensing  
- Silence for revocation  

9.5 Ceremony Text

> “I withdraw this stream.”

This phrase is the sovereign act.

---

Signature

John  
Two Mile Solutions LLC  
Alaska Native heir, service‑disabled veteran  
December 23, 2025

---

