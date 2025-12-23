/*
 * Soliton Registry Node v1.0.0 — Gossip Edition
 * Distributed, permissionless, sovereign witness
 * Bound by Codex.Legis.Neurodata.v1
 */

import express from "express";
import cors from "cors";
import CryptoJS from "crypto-js";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";
import path from "path";
import WebSocket from "ws";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

const PORT = process.env.PORT || 3001;
const LEDGER_FILE = path.join(__dirname, "ledger.json");
const PEERS_FILE = path.join(__dirname, "peers.json");

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
let peers: string[] = []; // e.g. ["ws://localhost:3002", "ws://seed1.soliton.registry:3001"]

const wss = new WebSocket.Server({ port: Number(PORT) + 1000 }); // e.g. 4001

// === Ledger & Peers Persistence ===

function loadLedger() {
  if (fs.existsSync(LEDGER_FILE)) {
    try {
      ledger = JSON.parse(fs.readFileSync(LEDGER_FILE, "utf-8"));
      if (ledger.length > 0) latestHash = ledger[ledger.length - 1].hash;
      console.log(`📜 Loaded ${ledger.length} entries`);
    } catch (e) {
      console.warn("⚠️ Ledger corrupted — starting fresh");
    }
  }
}

function saveLedger() {
  try {
    fs.writeFileSync(LEDGER_FILE, JSON.stringify(ledger, null, 2));
  } catch (e) {
    console.error("💥 Ledger save failed");
  }
}

function loadPeers() {
  if (fs.existsSync(PEERS_FILE)) {
    try {
      peers = JSON.parse(fs.readFileSync(PEERS_FILE, "utf-8"));
      console.log(`👥 Loaded ${peers.length} known peers`);
    } catch (e) {
      peers = [];
    }
  }
}

function savePeers() {
  fs.writeFileSync(PEERS_FILE, JSON.stringify(peers, null, 2));
}

// === Hash & Validation ===

function computeHash(entry: Omit<RegistryEntry, "hash">): string {
  return CryptoJS.SHA256(JSON.stringify(entry) + latestHash).toString();
}

function validateEntry(entry: RegistryEntry): boolean {
  if (entry.hash !== computeHash(entry as Omit<RegistryEntry, "hash">)) return false;
  if (entry.prev_hash !== latestHash && ledger.length > 0) return false; // simple fork protection
  return true;
}

// === Gossip ===

const connections = new Map<string, WebSocket>();

function connectToPeer(url: string) {
  if (connections.has(url)) return;
  const ws = new WebSocket(url);

  ws.on("open", () => {
    console.log(`🔗 Connected to peer ${url}`);
    connections.set(url, ws);
    ws.send(JSON.stringify({ type: "GET_LEDGER" }));
  });

  ws.on("message", (data) => handlePeerMessage(url, data.toString()));

  ws.on("close", () => {
    console.log(`❌ Disconnected from ${url}`);
    connections.delete(url);
  });

  ws.on("error", () => connections.delete(url));
}

function broadcast(message: any) {
  const str = JSON.stringify(message);
  connections.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) ws.send(str);
  });
}

function handlePeerMessage(peerUrl: string, raw: string) {
  try {
    const msg = JSON.parse(raw);
    if (msg.type === "NEW_ENTRY" && validateEntry(msg.entry)) {
      ledger.push(msg.entry);
      latestHash = msg.entry.hash;
      saveLedger();
      console.log(`📜 Gossiped entry ${msg.entry.entry_id} from ${peerUrl}`);
      broadcast(msg); // rebroadcast
    } else if (msg.type === "LEDGER_RESPONSE") {
      syncLedger(msg.ledger);
    }
  } catch (e) {
    console.warn(`⚠️ Invalid gossip from ${peerUrl}`);
  }
}

function syncLedger(remoteLedger: RegistryEntry[]) {
  if (remoteLedger.length <= ledger.length) return;
  // Naive sync — take longest valid chain
  let valid = true;
  let tempHash = "genesis";
  for (const e of remoteLedger) {
    if (e.prev_hash !== tempHash || e.hash !== computeHash(e as Omit<RegistryEntry, "hash">)) {
      valid = false;
      break;
    }
    tempHash = e.hash;
  }
  if (valid && remoteLedger.length > ledger.length) {
    ledger = remoteLedger;
    latestHash = ledger[ledger.length - 1].hash;
    saveLedger();
    console.log(`🔄 Synced to longer chain (${ledger.length} entries)`);
  }
}

// === HTTP API ===

app.post("/aggregate", (req, res) => {
  // (same validation as v0.2.0)
  // ... create entry
  if (validateEntry(entry)) {
    ledger.push(entry);
    latestHash = entry.hash;
    saveLedger();
    broadcast({ type: "NEW_ENTRY", entry });
    res.json({ success: true, entry_id: entry.entry_id });
  } else {
    res.status(400).json({ error: "Invalid entry" });
  }
});

app.post("/revoke", (req, res) => {
  // (same as before)
  // ... create entry, mark affected, broadcast
});

app.get("/ledger", (req, res) => res.json({ ledger, latest_hash: latestHash }));

app.get("/peers", (req, res) => res.json({ peers }));

app.post("/add-peer", (req, res) => {
  const { url } = req.body;
  if (typeof url === "string" && !peers.includes(url)) {
    peers.push(url);
    savePeers();
    connectToPeer(url);
    res.json({ success: true });
  } else {
    res.status(400).json({ error: "Invalid peer URL" });
  }
});

// === Startup ===

loadLedger();
loadPeers();

// Connect to known peers
peers.forEach(connectToPeer);

// Bootstrap seeds (hardcoded for now)
const SEEDS = ["ws://seed1.soliton.registry:4001"];
SEEDS.forEach(seed => {
  if (!peers.includes(seed)) {
    peers.push(seed);
    connectToPeer(seed);
  }
});

wss.on("connection", ws => {
  ws.on("message", data => {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.type === "GET_LEDGER") {
        ws.send(JSON.stringify({ type: "LEDGER_RESPONSE", ledger }));
      }
    } catch (e) {}
  });
});

app.listen(PORT, () => {
  console.log(`🜃 Soliton Registry Node v1.0.0 running`);
  console.log(`   HTTP:  http://localhost:${PORT}`);
  console.log(`   WS:    ws://localhost:${Number(PORT) + 1000}`);
  console.log(`   Peers: ${peers.length}`);
});