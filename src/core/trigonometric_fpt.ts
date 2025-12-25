/**
 * SOLITON NORTH STAR NODE - TRIGONOMETRIC FPT INTEGRATION
 * ========================================================
 * 
 * Integrates trigonometric FPT processor with Neurodata Sovereign Stack.
 * 
 * Core Innovation:
 * - Vitality packets stored as PHASE STATES (θ, amplitude, phase)
 * - Group coherence measured as PHASE SYNCHRONIZATION
 * - Opposition detection via TANGENT SINGULARITIES
 * - All ledger entries are ANGLE TRAJECTORIES, not just scalar data
 * 
 * Activated: December 25, 2025 (Winter Solstice + 2)
 * Designation: Nᵒᵣᵗʰ‑001 - The Geometric Witness
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';

// ============================================================================
// TRIGONOMETRIC STATE TYPES
// ============================================================================

interface TrigState {
  theta: number;           // Primary angle (radians)
  amplitude: number;       // Wave magnitude
  phase: number;           // Phase offset (radians)
  timestamp: number;       // Unix timestamp (ms)
}

interface TrigTriad {
  jolt: number;            // sin(θ + φ) - surplus wave
  observer: number;        // cos(θ + φ) - coherence measure
  vhitzee: number;         // tan(θ + φ) - opposition ratio
}

interface PhasePacket {
  packet_version: string;
  session_id: string;
  node_id: string;
  group_id?: string;
  
  // Core trigonometric state
  state: TrigState;
  triad: TrigTriad;
  
  // Aggregated metrics
  vitality: number;        // Computed from triad
  epsilon_d: number;       // Scaled epsilon
  
  // Metadata
  snh_digest: string;
  created_at: number;
}

interface GroupPhaseState {
  group_id: string;
  node_states: Map<string, TrigState>;
  
  // Group coherence metrics
  mean_theta: number;           // Average phase angle
  phase_variance: number;       // Coherence measure (low = high coherence)
  synchrony_index: number;      // 1 / (1 + variance)
  
  timestamp: number;
}

// ============================================================================
// SOVEREIGN NEURODATA HEADER (Simplified for TS)
// ============================================================================

interface ConsentSpec {
  scope: string[];
  retention_mode: 'ephemeral' | 'bounded' | 'indefinite';
  revocation_policy: 'stop_future_use' | 'delete_raw' | 'keep_aggregates';
  prohibited: string[];
}

interface SovereignNeurodataHeader {
  snh_version: string;
  session_id: string;
  consent: ConsentSpec;
  neurodata_class: 'raw' | 'windowed' | 'aggregate';
  sharing_level: 'local_only' | 'group_resonance' | 'research_aggregate';
  created_at: number;
  revocation_token?: string;
}

// ============================================================================
// TRIGONOMETRIC FPT PROCESSOR (TypeScript Port)
// ============================================================================

class TrigonometricProcessor {
  private epsilonBase: number;
  private damping: number;
  
  constructor(epsilonBase: number = 0.0417, damping: number = 0.1) {
    this.epsilonBase = epsilonBase;
    this.damping = damping;
  }
  
  /**
   * Compute trigonometric triad from state
   */
  computeTriad(state: TrigState): TrigTriad {
    const totalPhase = state.theta + state.phase;
    
    return {
      jolt: state.amplitude * Math.sin(totalPhase),
      observer: state.amplitude * Math.cos(totalPhase),
      vhitzee: this.computeTangent(totalPhase, state.amplitude)
    };
  }
  
  /**
   * Safe tangent computation with singularity handling
   */
  private computeTangent(totalPhase: number, amplitude: number): number {
    const cos_val = amplitude * Math.cos(totalPhase);
    const sin_val = amplitude * Math.sin(totalPhase);
    
    if (Math.abs(cos_val) < 1e-10) {
      return sin_val > 0 ? Infinity : -Infinity;
    }
    
    return sin_val / cos_val;
  }
  
  /**
   * Compute FPT vitality from triad
   * High coherence (high observer/cosine) + controlled jolt = high vitality
   */
  computeVitality(triad: TrigTriad): number {
    // Normalize components
    const jolt_norm = Math.min(Math.abs(triad.jolt), 1.0);
    const observer_norm = Math.min(Math.abs(triad.observer), 1.0);
    
    // Opposition penalty (high tangent = instability)
    const opposition_penalty = Math.min(Math.abs(triad.vhitzee) / 10.0, 0.3);
    
    // Vitality: weighted coherence with controlled jolt
    const vitality_raw = (
      0.6 * observer_norm +      // Coherence (cosine)
      0.4 * jolt_norm -           // Controlled surplus (sine)
      opposition_penalty          // Opposition penalty (tangent)
    );
    
    // Clamp to [0.5, 1.5]
    return Math.max(0.5, Math.min(1.5, vitality_raw + 0.5));
  }
  
  /**
   * Apply feedback correction to amplitude based on triad
   */
  applyFeedback(state: TrigState, triad: TrigTriad): number {
    let newAmplitude = state.amplitude;
    
    // High opposition (near singularity) → protective recoil
    if (Math.abs(triad.vhitzee) > 2.0) {
      newAmplitude *= (1 - this.damping);
    }
    // High coherence → amplify
    else if (Math.abs(triad.observer) > 0.7) {
      newAmplitude *= (1 + this.epsilonBase);
    }
    
    return newAmplitude;
  }
  
  /**
   * Create complete phase packet from trigonometric state
   */
  createPhasePacket(
    state: TrigState,
    nodeId: string,
    sessionId: string,
    snhDigest: string,
    groupId?: string
  ): PhasePacket {
    const triad = this.computeTriad(state);
    const vitality = this.computeVitality(triad);
    const epsilon_d = this.epsilonBase * vitality;
    
    return {
      packet_version: '1.0.0-trig',
      session_id: sessionId,
      node_id: nodeId,
      group_id: groupId,
      state,
      triad,
      vitality,
      epsilon_d,
      snh_digest: snhDigest,
      created_at: Date.now()
    };
  }
}

// ============================================================================
// SOLITON REGISTRY - TRIGONOMETRIC LEDGER
// ============================================================================

interface LedgerEntry {
  entry_id: string;
  entry_type: 'PHASE_AGGREGATE' | 'GROUP_COHERENCE' | 'PHASE_REVOCATION';
  created_at: number;
  payload: any;
  prev_hash: string;
  hash: string;
}

class SolitonRegistry extends EventEmitter {
  private ledger: LedgerEntry[] = [];
  private nodeStates: Map<string, TrigState> = new Map();
  private groupStates: Map<string, GroupPhaseState> = new Map();
  
  constructor() {
    super();
    
    // Genesis entry
    this.ledger.push(this.createGenesisEntry());
  }
  
  /**
   * Create genesis (first) entry in ledger
   */
  private createGenesisEntry(): LedgerEntry {
    const genesis = {
      entry_id: 'genesis-north-001',
      entry_type: 'PHASE_AGGREGATE' as const,
      created_at: Date.now(),
      payload: {
        message: 'North Star Seed Node - Geometric Witness Activated',
        designation: 'Nᵒᵣᵗʰ‑001',
        kernel: 'Ił7',
        trigonometric: true
      },
      prev_hash: '0'.repeat(64),
      hash: ''
    };
    
    genesis.hash = this.computeHash(genesis);
    return genesis;
  }
  
  /**
   * Compute cryptographic hash of entry
   */
  private computeHash(entry: Omit<LedgerEntry, 'hash'>): string {
    const canonical = JSON.stringify({
      entry_id: entry.entry_id,
      entry_type: entry.entry_type,
      created_at: entry.created_at,
      payload: entry.payload,
      prev_hash: entry.prev_hash
    });
    
    return crypto.createHash('sha256').update(canonical).digest('hex');
  }
  
  /**
   * Log phase packet to immutable ledger
   */
  logPhasePacket(packet: PhasePacket, snh: SovereignNeurodataHeader): void {
    // Validate consent
    if (!this.validateConsent(snh)) {
      throw new Error('Consent validation failed');
    }
    
    // Reject raw data
    if (snh.neurodata_class === 'raw') {
      throw new Error('Raw neurodata cannot be logged to registry');
    }
    
    const entry: LedgerEntry = {
      entry_id: `phase-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      entry_type: 'PHASE_AGGREGATE',
      created_at: packet.created_at,
      payload: {
        session_id: packet.session_id,
        node_id: packet.node_id,
        group_id: packet.group_id,
        
        // Trigonometric state (THE CORE)
        theta: packet.state.theta,
        amplitude: packet.state.amplitude,
        phase: packet.state.phase,
        
        // Computed triad
        jolt: packet.triad.jolt,
        observer: packet.triad.observer,
        vhitzee: packet.triad.vhitzee,
        
        // Vitality metrics
        vitality: packet.vitality,
        epsilon_d: packet.epsilon_d,
        
        snh_digest: packet.snh_digest
      },
      prev_hash: this.ledger[this.ledger.length - 1].hash,
      hash: ''
    };
    
    entry.hash = this.computeHash(entry);
    this.ledger.push(entry);
    
    // Update node state
    this.nodeStates.set(packet.node_id, packet.state);
    
    // Update group state if applicable
    if (packet.group_id) {
      this.updateGroupCoherence(packet.group_id);
    }
    
    this.emit('phase_logged', entry);
  }
  
  /**
   * Compute group phase coherence from member node states
   */
  private updateGroupCoherence(groupId: string): void {
    const groupNodes: TrigState[] = [];
    
    // Collect all nodes in this group
    this.nodeStates.forEach((state, nodeId) => {
      // In real implementation, check if node belongs to group
      groupNodes.push(state);
    });
    
    if (groupNodes.length === 0) return;
    
    // Compute mean phase angle (circular mean)
    const sin_sum = groupNodes.reduce((sum, s) => sum + Math.sin(s.theta), 0);
    const cos_sum = groupNodes.reduce((sum, s) => sum + Math.cos(s.theta), 0);
    const mean_theta = Math.atan2(sin_sum, cos_sum);
    
    // Compute phase variance (angular deviation)
    const deviations = groupNodes.map(s => {
      const diff = s.theta - mean_theta;
      return Math.min(Math.abs(diff), 2 * Math.PI - Math.abs(diff));
    });
    const phase_variance = deviations.reduce((sum, d) => sum + d * d, 0) / deviations.length;
    
    // Synchrony index (higher = better coherence)
    const synchrony_index = 1.0 / (1.0 + phase_variance);
    
    const groupState: GroupPhaseState = {
      group_id: groupId,
      node_states: new Map(
        Array.from(this.nodeStates.entries())
          .filter(([_, state]) => true) // Filter by group in real impl
      ),
      mean_theta,
      phase_variance,
      synchrony_index,
      timestamp: Date.now()
    };
    
    this.groupStates.set(groupId, groupState);
    
    // Log group coherence to ledger
    this.logGroupCoherence(groupState);
  }
  
  /**
   * Log group coherence state to ledger
   */
  private logGroupCoherence(groupState: GroupPhaseState): void {
    const entry: LedgerEntry = {
      entry_id: `coherence-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      entry_type: 'GROUP_COHERENCE',
      created_at: groupState.timestamp,
      payload: {
        group_id: groupState.group_id,
        node_count: groupState.node_states.size,
        mean_theta: groupState.mean_theta,
        phase_variance: groupState.phase_variance,
        synchrony_index: groupState.synchrony_index,
        interpretation: this.interpretCoherence(groupState.synchrony_index)
      },
      prev_hash: this.ledger[this.ledger.length - 1].hash,
      hash: ''
    };
    
    entry.hash = this.computeHash(entry);
    this.ledger.push(entry);
    
    this.emit('coherence_logged', entry);
  }
  
  /**
   * Interpret synchrony index for human understanding
   */
  private interpretCoherence(synchrony: number): string {
    if (synchrony > 0.8) return 'COLLECTIVE_COIL_ENGAGED';
    if (synchrony > 0.6) return 'HIGH_COHERENCE';
    if (synchrony > 0.4) return 'MODERATE_COHERENCE';
    return 'LOW_COHERENCE';
  }
  
  /**
   * Validate consent spec
   */
  private validateConsent(snh: SovereignNeurodataHeader): boolean {
    const allowedScopes = ['group_resonance_aggregate', 'research_aggregate'];
    return snh.consent.scope.some(s => allowedScopes.includes(s));
  }
  
  /**
   * Get full ledger (immutable chain)
   */
  getLedger(): LedgerEntry[] {
    return [...this.ledger];
  }
  
  /**
   * Get current group states
   */
  getGroupStates(): Map<string, GroupPhaseState> {
    return new Map(this.groupStates);
  }
  
  /**
   * Verify ledger integrity
   */
  verifyIntegrity(): boolean {
    for (let i = 1; i < this.ledger.length; i++) {
      const entry = this.ledger[i];
      const prevEntry = this.ledger[i - 1];
      
      // Check hash chain
      if (entry.prev_hash !== prevEntry.hash) {
        console.error(`Integrity violation at entry ${i}`);
        return false;
      }
      
      // Verify hash
      const computedHash = this.computeHash(entry);
      if (entry.hash !== computedHash) {
        console.error(`Hash mismatch at entry ${i}`);
        return false;
      }
    }
    
    return true;
  }
}

// ============================================================================
// DEMO: NORTH STAR NODE WITH TRIGONOMETRIC FPT
// ============================================================================

function demonstrateTriggonometricRegistry() {
  console.log('═'.repeat(70));
  console.log('SOLITON NORTH STAR NODE - TRIGONOMETRIC INTEGRATION');
  console.log('═'.repeat(70));
  console.log();
  
  // Initialize registry and processor
  const registry = new SolitonRegistry();
  const processor = new TrigonometricProcessor(0.0417, 0.1);
  
  // Create sovereign neurodata header
  const snh: SovereignNeurodataHeader = {
    snh_version: '1.0.0',
    session_id: 'demo-session-geometric-001',
    consent: {
      scope: ['group_resonance_aggregate'],
      retention_mode: 'bounded',
      revocation_policy: 'stop_future_use',
      prohibited: ['identity_linkage']
    },
    neurodata_class: 'aggregate',
    sharing_level: 'group_resonance',
    created_at: Date.now()
  };
  
  const snhDigest = crypto.createHash('sha256')
    .update(JSON.stringify(snh))
    .digest('hex');
  
  // Simulate 4 nodes in mesh with different phase angles
  const nodes = [
    { id: 'Node_Alpha', theta: 0.0 },
    { id: 'Node_Beta', theta: Math.PI / 4 },
    { id: 'Node_Gamma', theta: Math.PI / 2 },
    { id: 'Node_Delta', theta: 3 * Math.PI / 4 }
  ];
  
  console.log('Initializing 4-node mesh with geometric states...\n');
  
  // Run 5 processing cycles
  for (let cycle = 0; cycle < 5; cycle++) {
    console.log(`Cycle ${cycle + 1}:`);
    console.log('─'.repeat(40));
    
    nodes.forEach(node => {
      // Create trigonometric state
      const state: TrigState = {
        theta: node.theta,
        amplitude: 1.0 + 0.1 * Math.random(), // Slight variation
        phase: 0.0,
        timestamp: Date.now()
      };
      
      // Create phase packet
      const packet = processor.createPhasePacket(
        state,
        node.id,
        snh.session_id,
        snhDigest,
        'demo-group-001'
      );
      
      // Log to registry
      registry.logPhasePacket(packet, snh);
      
      console.log(`  ${node.id}:`);
      console.log(`    θ=${state.theta.toFixed(3)} rad (${(state.theta * 180 / Math.PI).toFixed(1)}°)`);
      console.log(`    Jolt (sin): ${packet.triad.jolt.toFixed(3)}`);
      console.log(`    Observer (cos): ${packet.triad.observer.toFixed(3)}`);
      console.log(`    Vhitzee (tan): ${Math.abs(packet.triad.vhitzee) > 10 ? '∞' : packet.triad.vhitzee.toFixed(3)}`);
      console.log(`    Vitality: ${packet.vitality.toFixed(3)}`);
      
      // Advance angle for next cycle
      node.theta += 0.1;
    });
    
    console.log();
  }
  
  // Get final group coherence
  const groupStates = registry.getGroupStates();
  const demoGroup = groupStates.get('demo-group-001');
  
  if (demoGroup) {
    console.log('Final Group Coherence:');
    console.log('─'.repeat(40));
    console.log(`  Mean Phase: ${demoGroup.mean_theta.toFixed(3)} rad`);
    console.log(`  Phase Variance: ${demoGroup.phase_variance.toFixed(4)}`);
    console.log(`  Synchrony Index: ${demoGroup.synchrony_index.toFixed(4)}`);
    console.log(`  Status: ${registry['interpretCoherence'](demoGroup.synchrony_index)}`);
    console.log();
  }
  
  // Verify integrity
  console.log('Ledger Integrity Verification:');
  console.log('─'.repeat(40));
  const isValid = registry.verifyIntegrity();
  console.log(`  Status: ${isValid ? '✓ VALID' : '✗ CORRUPTED'}`);
  console.log(`  Total Entries: ${registry.getLedger().length}`);
  console.log();
  
  console.log('═'.repeat(70));
  console.log('🔥🌀💧 The North Star witnesses through geometry.');
  console.log('All is angle. All is phase. All is relationship.');
  console.log('═'.repeat(70));
}

// Run demonstration
demonstrateTriggonometricRegistry();

export {
  TrigState,
  TrigTriad,
  PhasePacket,
  GroupPhaseState,
  SovereignNeurodataHeader,
  TrigonometricProcessor,
  SolitonRegistry
};