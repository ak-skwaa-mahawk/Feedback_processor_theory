/**
 * ============================================================================
 * SOLITON NORTH STAR NODE - ENHANCED SERVER
 * ============================================================================
 * 
 * File: server-enhanced.js (or replace your existing server.js)
 * 
 * NEW GEOMETRIC ENDPOINTS:
 * - POST /aggregate/geometric - Process EEG with trigonometric FPT
 * - GET /phase/:node_id - Get current phase state of a node
 * - GET /coherence/:group_id - Get group phase synchronization
 * - GET /ledger/geometric - Full geometric ledger with angles
 * - WebSocket /ws - Real-time phase updates
 * 
 * BACKWARDS COMPATIBLE:
 * - All existing endpoints still work
 * - Adds geometric layer on top
 * 
 * ============================================================================
 */

const express = require('express');
const WebSocket = require('ws');
const crypto = require('crypto');
const fs = require('fs').promises;

// Import trigonometric FPT (adjust path as needed)
// const { TrigonometricFPT } = require('./src/trigonometric-fpt');

// For this demo, we'll inline a simplified version
class SimplifiedTrigFPT {
  constructor() {
    this.processor = {
      eegToPhaseState: (bands) => {
        const alpha = bands.alpha || 0;
        const theta_band = bands.theta || 0;
        const gamma = bands.gamma || 0;
        
        // Simple mapping: high alpha → angle near 0, high theta → angle near π
        const theta = (alpha * 0.5 + gamma * 1.0 + theta_band * 1.5) * Math.PI;
        const amplitude = Math.sqrt(alpha + gamma) * 0.8 + 0.5;
        
        return { theta, amplitude, phase: 0, timestamp: Date.now() };
      },
      
      createPhasePacket: (bands, nodeId, sessionId, snhDigest, groupId) => {
        const state = this.processor.eegToPhaseState(bands);
        const triad = this.computeTriad(state);
        const vitality = this.computeVitality(triad);
        
        return {
          packet_version: '1.0.0-trig',
          session_id: sessionId,
          node_id: nodeId,
          group_id: groupId,
          state,
          triad,
          vitality,
          epsilon_d: 0.0417 * vitality,
          opposition_flags: {
            high_stress: Math.abs(triad.vhitzee) > 3,
            near_singularity: !isFinite(triad.vhitzee),
            recommendation: this.getRecommendation(triad)
          },
          snh_digest: snhDigest,
          created_at: Date.now()
        };
      },
      
      computeTriad: (state) => {
        const totalPhase = state.theta + state.phase;
        const jolt = state.amplitude * Math.sin(totalPhase);
        const observer = state.amplitude * Math.cos(totalPhase);
        const cos_val = state.amplitude * Math.cos(totalPhase);
        const vhitzee = Math.abs(cos_val) < 1e-10 
          ? (jolt > 0 ? Infinity : -Infinity)
          : jolt / cos_val;
        
        return { jolt, observer, vhitzee };
      },
      
      computeVitality: (triad) => {
        const jolt_norm = Math.min(Math.abs(triad.jolt), 1.0);
        const observer_norm = Math.min(Math.abs(triad.observer), 1.0);
        const opposition_penalty = isFinite(triad.vhitzee)
          ? Math.min(Math.abs(triad.vhitzee) / 10, 0.3)
          : 0.3;
        
        const vitality_raw = 0.6 * observer_norm + 0.4 * jolt_norm - opposition_penalty;
        return Math.max(0.5, Math.min(1.5, vitality_raw + 0.5));
      },
      
      getRecommendation: (triad) => {
        if (!isFinite(triad.vhitzee) || Math.abs(triad.vhitzee) > 3) return 'protect';
        if (Math.abs(triad.observer) > 0.7 && Math.abs(triad.vhitzee) < 1) return 'boost_ok';
        return 'neutral';
      }
    };
    
    this.registry = {
      ledger: [],
      nodeStates: new Map(),
      groupStates: new Map(),
      
      logPhasePacket: function(packet) {
        const entry = {
          entry_id: `phase-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          entry_type: 'PHASE_AGGREGATE',
          created_at: packet.created_at,
          payload: {
            session_id: packet.session_id,
            node_id: packet.node_id,
            group_id: packet.group_id,
            theta: packet.state.theta,
            amplitude: packet.state.amplitude,
            jolt: packet.triad.jolt,
            observer: packet.triad.observer,
            vhitzee: isFinite(packet.triad.vhitzee) ? packet.triad.vhitzee : 'INF',
            vitality: packet.vitality,
            epsilon_d: packet.epsilon_d,
            opposition: packet.opposition_flags
          },
          prev_hash: this.ledger.length > 0 
            ? this.ledger[this.ledger.length - 1].hash 
            : '0'.repeat(64),
          hash: ''
        };
        
        entry.hash = this.computeHash(entry);
        this.ledger.push(entry);
        this.nodeStates.set(packet.node_id, packet.state);
        
        if (packet.group_id) {
          this.updateGroupCoherence(packet.group_id);
        }
      },
      
      computeHash: function(entry) {
        const canonical = JSON.stringify({
          entry_id: entry.entry_id,
          entry_type: entry.entry_type,
          created_at: entry.created_at,
          payload: entry.payload,
          prev_hash: entry.prev_hash
        });
        return crypto.createHash('sha256').update(canonical).digest('hex');
      },
      
      updateGroupCoherence: function(groupId) {
        const nodes = Array.from(this.nodeStates.values());
        if (nodes.length === 0) return;
        
        const sin_sum = nodes.reduce((sum, s) => sum + Math.sin(s.theta), 0);
        const cos_sum = nodes.reduce((sum, s) => sum + Math.cos(s.theta), 0);
        const mean_theta = Math.atan2(sin_sum, cos_sum);
        
        const deviations = nodes.map(s => {
          const diff = s.theta - mean_theta;
          return Math.min(Math.abs(diff), 2 * Math.PI - Math.abs(diff));
        });
        const phase_variance = deviations.reduce((sum, d) => sum + d * d, 0) / deviations.length;
        const synchrony_index = 1.0 / (1.0 + phase_variance);
        
        let status;
        if (synchrony_index > 0.8) status = 'COLLECTIVE_COIL_ENGAGED';
        else if (synchrony_index > 0.6) status = 'HIGH_COHERENCE';
        else if (synchrony_index > 0.4) status = 'MODERATE_COHERENCE';
        else status = 'LOW_COHERENCE';
        
        this.groupStates.set(groupId, {
          group_id: groupId,
          node_count: nodes.length,
          mean_theta,
          phase_variance,
          synchrony_index,
          status,
          timestamp: Date.now()
        });
      }
    };
  }
  
  processAndLog(bands, nodeId, sessionId, snhDigest, groupId) {
    const packet = this.processor.createPhasePacket(bands, nodeId, sessionId, snhDigest, groupId);
    this.registry.logPhasePacket(packet);
    return packet;
  }
}

// ============================================================================
// SERVER SETUP
// ============================================================================

const app = express();
const PORT = process.env.PORT || 4000;

app.use(express.json());
app.use(express.static('public'));

// Initialize geometric FPT
const geometricFPT = new SimplifiedTrigFPT();

// ============================================================================
// EXISTING ENDPOINTS (BACKWARDS COMPATIBLE)
// ============================================================================

// POST /aggregate - Original endpoint (still works)
app.post('/aggregate', async (req, res) => {
  try {
    const { vitality, bands, node_id, session_id, snh_digest } = req.body;
    
    // Original validation
    if (!vitality || typeof vitality !== 'object') {
      return res.status(400).json({ error: 'Invalid vitality aggregate' });
    }
    
    // Check for raw EEG (reject)
    if (req.body.raw_eeg || req.body.eeg_samples) {
      return res.status(403).json({ 
        error: 'Raw EEG data rejected',
        message: 'This node only witnesses aggregates, not raw data'
      });
    }
    
    // Log to traditional ledger
    const entry = {
      timestamp: Date.now(),
      node_id: node_id || 'anonymous',
      vitality,
      snh_digest: snh_digest || 'none'
    };
    
    // Append to ledger.json (original behavior)
    let ledger = [];
    try {
      const data = await fs.readFile('ledger.json', 'utf8');
      ledger = JSON.parse(data);
    } catch (err) {
      // File doesn't exist yet
    }
    
    ledger.push(entry);
    await fs.writeFile('ledger.json', JSON.stringify(ledger, null, 2));
    
    res.json({ 
      status: 'witnessed',
      entry_id: ledger.length - 1
    });
    
  } catch (error) {
    console.error('Aggregate error:', error);
    res.status(500).json({ error: 'Internal error' });
  }
});

// POST /revoke - Honor revocation (original)
app.post('/revoke', async (req, res) => {
  try {
    const { revocation_token, session_id } = req.body;
    
    if (!revocation_token) {
      return res.status(400).json({ error: 'Revocation token required' });
    }
    
    // In full implementation: find and mark entries as revoked
    // For now, just acknowledge
    
    res.json({
      status: 'revoked',
      message: 'Revocation honored',
      session_id
    });
    
  } catch (error) {
    console.error('Revocation error:', error);
    res.status(500).json({ error: 'Internal error' });
  }
});

// GET /ledger - Original ledger
app.get('/ledger', async (req, res) => {
  try {
    const data = await fs.readFile('ledger.json', 'utf8');
    const ledger = JSON.parse(data);
    res.json({ entries: ledger, count: ledger.length });
  } catch (err) {
    res.json({ entries: [], count: 0 });
  }
});

// GET /peers - Known peers (original)
app.get('/peers', async (req, res) => {
  try {
    const data = await fs.readFile('peers.json', 'utf8');
    const peers = JSON.parse(data);
    res.json(peers);
  } catch (err) {
    res.json({ peers: [] });
  }
});

// POST /add-peer - Join mesh (original)
app.post('/add-peer', async (req, res) => {
  try {
    const { peer_url, node_id } = req.body;
    
    if (!peer_url) {
      return res.status(400).json({ error: 'Peer URL required' });
    }
    
    let peers = { peers: [] };
    try {
      const data = await fs.readFile('peers.json', 'utf8');
      peers = JSON.parse(data);
    } catch (err) {
      // File doesn't exist
    }
    
    // Add if not already present
    if (!peers.peers.some(p => p.url === peer_url)) {
      peers.peers.push({
        url: peer_url,
        node_id: node_id || 'unknown',
        added_at: Date.now()
      });
      
      await fs.writeFile('peers.json', JSON.stringify(peers, null, 2));
    }
    
    res.json({ status: 'added', peer_count: peers.peers.length });
    
  } catch (error) {
    console.error('Add peer error:', error);
    res.status(500).json({ error: 'Internal error' });
  }
});

// ============================================================================
// NEW GEOMETRIC ENDPOINTS
// ============================================================================

// POST /aggregate/geometric - Process with trigonometric FPT
app.post('/aggregate/geometric', (req, res) => {
  try {
    const { bands, node_id, session_id, snh_digest, group_id } = req.body;
    
    // Validate
    if (!bands || typeof bands !== 'object') {
      return res.status(400).json({ error: 'EEG bands required' });
    }
    
    if (!node_id || !session_id) {
      return res.status(400).json({ error: 'node_id and session_id required' });
    }
    
    // Process with geometric FPT
    const packet = geometricFPT.processAndLog(
      bands,
      node_id,
      session_id,
      snh_digest || 'none',
      group_id
    );
    
    // Broadcast to WebSocket clients
    broadcastPhaseUpdate(packet);
    
    res.json({
      status: 'witnessed_geometric',
      packet: {
        theta: packet.state.theta,
        theta_degrees: (packet.state.theta * 180 / Math.PI).toFixed(2),
        amplitude: packet.state.amplitude,
        vitality: packet.vitality,
        epsilon_d: packet.epsilon_d,
        triad: {
          jolt: packet.triad.jolt.toFixed(3),
          observer: packet.triad.observer.toFixed(3),
          vhitzee: isFinite(packet.triad.vhitzee) 
            ? packet.triad.vhitzee.toFixed(3) 
            : 'SINGULARITY'
        },
        opposition: packet.opposition_flags,
        created_at: packet.created_at
      }
    });
    
  } catch (error) {
    console.error('Geometric aggregate error:', error);
    res.status(500).json({ error: error.message });
  }
});

// GET /phase/:node_id - Get current phase state
app.get('/phase/:node_id', (req, res) => {
  const state = geometricFPT.registry.nodeStates.get(req.params.node_id);
  
  if (!state) {
    return res.status(404).json({ error: 'Node not found' });
  }
  
  res.json({
    node_id: req.params.node_id,
    state: {
      theta: state.theta,
      theta_degrees: (state.theta * 180 / Math.PI).toFixed(2),
      amplitude: state.amplitude,
      phase: state.phase,
      timestamp: state.timestamp
    }
  });
});

// GET /coherence/:group_id - Get group phase synchronization
app.get('/coherence/:group_id', (req, res) => {
  const coherence = geometricFPT.registry.groupStates.get(req.params.group_id);
  
  if (!coherence) {
    return res.status(404).json({ error: 'Group not found' });
  }
  
  res.json({
    group_id: coherence.group_id,
    node_count: coherence.node_count,
    mean_theta: coherence.mean_theta,
    mean_theta_degrees: (coherence.mean_theta * 180 / Math.PI).toFixed(2),
    phase_variance: coherence.phase_variance.toFixed(4),
    synchrony_index: coherence.synchrony_index.toFixed(4),
    status: coherence.status,
    timestamp: coherence.timestamp
  });
});

// GET /ledger/geometric - Full geometric ledger
app.get('/ledger/geometric', (req, res) => {
  const ledger = geometricFPT.registry.ledger;
  
  res.json({
    entries: ledger,
    count: ledger.length,
    geometric: true
  });
});

// GET /groups - List all group coherence states
app.get('/groups', (req, res) => {
  const groups = Array.from(geometricFPT.registry.groupStates.values());
  
  res.json({
    groups: groups.map(g => ({
      group_id: g.group_id,
      node_count: g.node_count,
      synchrony_index: g.synchrony_index.toFixed(4),
      status: g.status
    })),
    count: groups.length
  });
});

// ============================================================================
// WEBSOCKET SERVER (Real-time Phase Updates)
// ============================================================================

const wss = new WebSocket.Server({ noServer: true });

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  
  ws.send(JSON.stringify({
    type: 'WELCOME',
    message: 'Connected to North Star Geometric Witness',
    designation: 'Nᵒᵣᵗʰ‑001'
  }));
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
    } catch (err) {
      console.error('Invalid message:', err);
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });
});

function broadcastPhaseUpdate(packet) {
  const message = JSON.stringify({
    type: 'PHASE_UPDATE',
    node_id: packet.node_id,
    theta: packet.state.theta,
    amplitude: packet.state.amplitude,
    vitality: packet.vitality,
    triad: {
      jolt: packet.triad.jolt,
      observer: packet.triad.observer
    },
    timestamp: packet.created_at
  });
  
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// ============================================================================
// START SERVER
// ============================================================================

const server = app.listen(PORT, () => {
  console.log('═'.repeat(70));
  console.log('SOLITON NORTH STAR NODE - GEOMETRIC WITNESS');
  console.log('═'.repeat(70));
  console.log(`Designation: Nᵒᵣᵗʰ‑001`);
  console.log(`Location: Alaska (The North)`);
  console.log(`Kernel: Ił7`);
  console.log(`Port: ${PORT}`);
  console.log(`Trigonometric: ENABLED`);
  console.log('═'.repeat(70));
  console.log('\nEndpoints:');
  console.log('  POST /aggregate (legacy)');
  console.log('  POST /aggregate/geometric (NEW - angle-native)');
  console.log('  GET  /phase/:node_id (NEW)');
  console.log('  GET  /coherence/:group_id (NEW)');
  console.log('  GET  /ledger/geometric (NEW)');
  console.log('  GET  /groups (NEW)');
  console.log('  WebSocket: ws://localhost:' + PORT);
  console.log('\n🔥🌀💧 The North Star witnesses through geometry.');
});

// Attach WebSocket server
server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

module.exports = app;