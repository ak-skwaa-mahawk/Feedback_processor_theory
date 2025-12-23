// === Hashcash PoW Configuration ===

const POW_DIFFICULTY = 18; // number of leading zero bits (18 ≈ 0.5–2s on modern phone)
const POW_MAX_AGE_SECONDS = 120; // challenge valid for 2 minutes

interface PowChallenge {
  challenge_string: string; // base for proof
  difficulty: number;
  issued_at: number;     // unix seconds
}

const activeChallenges = new Map<string, PowChallenge>(); // client_ip → challenge (rate-limited)

// Generate challenge string (unique per request)
function generateChallenge(clientIp: string): PowChallenge {
  const issued_at = Math.floor(Date.now() / 1000);
  const challenge_string = `\( {clientIp}: \){issued_at}:${uuidv4()}`;
  const challenge: PowChallenge = { challenge_string, difficulty: POW_DIFFICULTY, issued_at };
  activeChallenges.set(clientIp, challenge);
  // Cleanup old challenges
  setTimeout(() => activeChallenges.delete(clientIp), POW_MAX_AGE_SECONDS * 1000);
  return challenge;
}

// Verify Hashcash solution
function verifyPow(challenge_string: string, nonce: number | string): boolean {
  const hash = CryptoJS.SHA256(challenge_string + nonce.toString()).toString();
  const bits = parseInt(hash, 16).toString(2).padStart(256, '0');
  return bits.startsWith('0'.repeat(POW_DIFFICULTY));
}

// === New Endpoint: GET /pow-challenge ===

app.get("/pow-challenge", (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || "unknown";
  const challenge = generateChallenge(clientIp);
  res.json({
    challenge_string: challenge.challenge_string,
    difficulty: challenge.difficulty,
    max_age_seconds: POW_MAX_AGE_SECONDS,
    message: "Solve Hashcash PoW before submitting entries"
  });
});

// === Updated POST /aggregate (with PoW) ===

app.post("/aggregate", (req, res) => {
  try {
    const { snh_digest, vitality_packet, payload_summary, pow_nonce, challenge_string } = req.body;

    const clientIp = req.ip || "unknown";

    // PoW check first
    if (!challenge_string || pow_nonce === undefined) {
      return res.status(400).json({
        error: "POW_REQUIRED",
        message: "Proof-of-work required. GET /pow-challenge first."
      });
    }

    const storedChallenge = activeChallenges.get(clientIp);
    if (!storedChallenge || storedChallenge.challenge_string !== challenge_string) {
      return res.status(400).json({ error: "INVALID_CHALLENGE", message: "Unknown or expired challenge" });
    }

    const age = Math.floor(Date.now() / 1000) - storedChallenge.issued_at;
    if (age > POW_MAX_AGE_SECONDS) {
      return res.status(400).json({ error: "CHALLENGE_EXPIRED", message: "Challenge too old" });
    }

    if (!verifyPow(challenge_string, pow_nonce)) {
      return res.status(400).json({ error: "INVALID_POW", message: "Proof-of-work invalid" });
    }

    // PoW valid — clear challenge
    activeChallenges.delete(clientIp);

    // Now proceed with aggregate validation
    const vitality_packet_hash = CryptoJS.SHA256(JSON.stringify(vitality_packet || {})).toString();

    if (!validateAggregatePayload({
      snh_digest,
      vitality_packet_hash,
      summary: payload_summary
    })) {
      return res.status(403).json({
        error: "INVALID_AGGREGATE",
        message: "Aggregate validation failed per Codex.Legis.Neurodata.v1"
      });
    }

    const entry: RegistryEntry = {
      entry_id: `reg-${uuidv4().slice(0, 8)}`,
      entry_type: "EEG_AGGREGATE",
      created_at_utc: new Date().toISOString(),
      payload: {
        snh_digest,
        vitality_packet_hash,
        summary: payload_summary,
        flags: { revoked: false }
      },
      prev_hash: latestHash,
      hash: "",
    };

    entry.hash = computeHash(entry);

    if (!validateEntry(entry)) {
      return res.status(500).json({ error: "CHAIN_ERROR", message: "Failed to append to chain" });
    }

    ledger.push(entry);
    latestHash = entry.hash;
    saveLedger();
    broadcast({ type: "NEW_ENTRY", entry });

    console.log(`📜 EEG_AGGREGATE witnessed (PoW verified): ${entry.entry_id}`);

    res.json({
      success: true,
      entry_id: entry.entry_id,
      hash: entry.hash,
      message: "Aggregate witnessed — PoW accepted"
    });
  } catch (err) {
    console.error("💥 Aggregate error:", err);
    res.status(500).json({ error: "INTERNAL_ERROR" });
  }
});

// === Updated POST /revoke (with PoW) ===

app.post("/revoke", (req, res) => {
  try {
    const { revocation_token_hash, session_ids, pow_nonce, challenge_string } = req.body;

    const clientIp = req.ip || "unknown";

    // Same PoW flow as aggregate
    if (!challenge_string || pow_nonce === undefined) {
      return res.status(400).json({ error: "POW_REQUIRED" });
    }

    const storedChallenge = activeChallenges.get(clientIp);
    if (!storedChallenge || storedChallenge.challenge_string !== challenge_string) {
      return res.status(400).json({ error: "INVALID_CHALLENGE" });
    }

    if ((Math.floor(Date.now() / 1000) - storedChallenge.issued_at) > POW_MAX_AGE_SECONDS) {
      return res.status(400).json({ error: "CHALLENGE_EXPIRED" });
    }

    if (!verifyPow(challenge_string, pow_nonce)) {
      return res.status(400).json({ error: "INVALID_POW" });
    }

    activeChallenges.delete(clientIp);

    // Revocation validation (same as before)
    if (!revocation_token_hash || !Array.isArray(session_ids) || session_ids.length === 0) {
      return res.status(400).json({ error: "INVALID_REVOCATION" });
    }

    // ... rest identical to previous revoke logic ...

    console.log(`🔥 EEG_REVOCATION witnessed (PoW verified): ${entry.entry_id}`);

    res.json({
      success: true,
      entry_id: entry.entry_id,
      records_affected: affected,
      message: "Revocation honored — PoW accepted"
    });
  } catch (err) {
    res.status(500).json({ error: "INTERNAL_ERROR" });
  }
});