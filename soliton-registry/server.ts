/*
 * Soliton Registry Mock Server — v0.2.0
 * Now with sovereign error handling
 * Bound by Codex.Legis.Neurodata.v1
 */

import express from "express";
import cors from "cors";
import CryptoJS from "crypto-js";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";
import path from "path";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

const LEDGER_FILE = path.join(__dirname, "ledger.json");

interface RegistryEntry {
  entry_id: string;
  entry_type: "EEG_AGGREGATE" | "EEG_REVOCATION";
  created_at_utc: string;
  payload: any;
  prev_hash: string;
  hash: string;
}

let ledger: RegistryEntry[] = [];
let latestHash = "genesis";

// Load ledger safely
function loadLedger() {
  if (!fs.existsSync(LEDGER_FILE)) {
    console.log("📜 No ledger file found — starting with genesis");
    return;
  }

  try {
    const data = fs.readFileSync(LEDGER_FILE, "utf-8");
    const parsed = JSON.parse(data);
    if (!Array.isArray(parsed)) throw new Error("Ledger is not an array");
    ledger = parsed;
    if (ledger.length > 0) {
      latestHash = ledger[ledger.length - 1].hash;
    }
    console.log(`📜 Loaded ${ledger.length} entries from ledger`);
  } catch (err) {
    console.error("⚠️ Failed to load ledger — starting fresh (corrupted or incompatible)");
    console.error(err instanceof Error ? err.message : err);
    ledger = [];
    latestHash = "genesis";
  }
}

loadLedger();

function saveLedger() {
  try {
    fs.writeFileSync(LEDGER_FILE, JSON.stringify(ledger, null, 2));
  } catch (err) {
    console.error("💥 CRITICAL: Failed to persist ledger to disk");
    console.error(err instanceof Error ? err.message : err);
    // We continue running — the ledger remains in memory
  }
}

function computeHash(entry: Omit<RegistryEntry, "hash">): string {
  const str = JSON.stringify(entry) + latestHash;
  return CryptoJS.SHA256(str).toString();
}

// Global error types
type RegistryError =
  | "INVALID_REQUEST"
  | "RAW_DATA_PROHIBITED"
  | "MISSING_SNH"
  | "INVALID_REVOCATION"
  | "INTERNAL_ERROR";

function sendError(res: express.Response, code: number, type: RegistryError, message: string) {
  console.warn(`❌ ${type}: ${message}`);
  res.status(code).json({
    success: false,
    error: type,
    message,
    // No stack traces or internals exposed
  });
}

// POST /aggregate
app.post("/aggregate", (req, res) => {
  try {
    const { snh_digest, vitality_packet, payload_summary } = req.body;

    if (!snh_digest || typeof snh_digest !== "string") {
      return sendError(res, 400, "MISSING_SNH", "Sovereign Neurodata Header digest required");
    }

    if (!vitality_packet || typeof vitality_packet !== "object") {
      return sendError(res, 400, "INVALID_REQUEST", "Vitality packet required");
    }

    if (payload_summary?.granularity === "raw") {
      return sendError(res, 403, "RAW_DATA_PROHIBITED", "Raw EEG prohibited by Codex.Legis.Neurodata.v1 §3");
    }

    const entry: RegistryEntry = {
      entry_id: `reg-${uuidv4().slice(0, 8)}`,
      entry_type: "EEG_AGGREGATE",
      created_at_utc: new Date().toISOString(),
      payload: {
        snh_digest,
        vitality_packet_hash: CryptoJS.SHA256(JSON.stringify(vitality_packet)).toString(),
        summary: payload_summary || {},
        flags: { revoked: false }
      },
      prev_hash: latestHash,
      hash: "",
    };

    entry.hash = computeHash(entry);
    latestHash = entry.hash;

    ledger.push(entry);
    saveLedger();

    console.log(`📜 EEG_AGGREGATE recorded: ${entry.entry_id}`);

    res.json({
      success: true,
      entry_id: entry.entry_id,
      hash: entry.hash,
      message: "Aggregate witnessed"
    });
  } catch (err) {
    sendError(res, 500, "INTERNAL_ERROR", "Failed to witness aggregate");
  }
});

// POST /revoke
app.post("/revoke", (req, res) => {
  try {
    const { revocation_token_hash, session_ids } = req.body;

    if (!revocation_token_hash || typeof revocation_token_hash !== "string") {
      return sendError(res, 400, "INVALID_REVOCATION", "Revocation token hash required");
    }

    if (!Array.isArray(session_ids) || session_ids.some(s => typeof s !== "string")) {
      return sendError(res, 400, "INVALID_REVOCATION", "Valid session_ids array required");
    }

    if (session_ids.length === 0) {
      return sendError(res, 400, "INVALID_REVOCATION", "At least one session_id must be specified");
    }

    const entry: RegistryEntry = {
      entry_id: `rev-${uuidv4().slice(0, 8)}`,
      entry_type: "EEG_REVOCATION",
      created_at_utc: new Date().toISOString(),
      payload: {
        revocation_token_hash,
        session_ids,
        action: "stop_future_use",
        records_affected: 0 // will count below
      },
      prev_hash: latestHash,
      hash: "",
    };

    // Count and mark affected aggregates
    let affected = 0;
    ledger = ledger.map(e => {
      if (
        e.entry_type === "EEG_AGGREGATE" &&
        session_ids.includes(e.payload.summary?.session_id || "")
      ) {
        e.payload.flags.revoked = true;
        affected++;
      }
      return e;
    });

    entry.payload.records_affected = affected;
    entry.hash = computeHash(entry);
    latestHash = entry.hash;

    ledger.push(entry);
    saveLedger();

    console.log(`🔥 EEG_REVOCATION recorded: ${entry.entry_id} — ${affected} records affected`);

    res.json({
      success: true,
      entry_id: entry.entry_id,
      hash: entry.hash,
      records_affected: affected,
      message: "Revocation honored and witnessed"
    });
  } catch (err) {
    sendError(res, 500, "INTERNAL_ERROR", "Failed to witness revocation");
  }
});

// GET /ledger
app.get("/ledger", (req, res) => {
  try {
    res.json({
      ledger,
      latest_hash: latestHash,
      total_entries: ledger.length
    });
  } catch (err) {
    sendError(res, 500, "INTERNAL_ERROR", "Failed to retrieve ledger");
  }
});

// Global unhandled error fallback
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error("💥 Unhandled error:", err);
  sendError(res, 500, "INTERNAL_ERROR", "Unexpected registry failure");
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`🜃 Soliton Registry Mock v0.2.0 running on http://localhost:${PORT}`);
  console.log(`   POST /aggregate   → witness vitality aggregate`);
  console.log(`   POST /revoke      → witness revocation`);
  console.log(`   GET  /ledger      → view immutable chain`);
  console.log(`\n   Ledger file: ${LEDGER_FILE}`);
});
interface RegistryEntry {
  entry_id: string;                // UUID-based
  entry_type: "EEG_AGGREGATE" | "EEG_REVOCATION";
  created_at_utc: string;          // ISO timestamp
  payload: {
    snh_digest: string;            // SHA-256 of Sovereign Neurodata Header
    // For AGGREGATE
    vitality_packet_hash?: string;
    summary?: any;                 // band means, vitality stats (no raw)
    flags?: { revoked: boolean };
    // For REVOCATION
    revocation_token_hash?: string;
    session_ids?: string[];
    action: "stop_future_use";
    records_affected?: number;
  };
  prev_hash: string;               // Links to previous global entry
  hash: string;                    // SHA-256 of entire entry + prev_hash
}
seeds.soliton.registry: [
  "seed1.soliton.registry:3001",
  "seed2.soliton.registry:3001",
  ...
]