// lib/relational_mesh_bridge.dart
// networkXG Sovereign Bridge — AGŁG v89 (Hardened)
// Matches the current Rust sovereign_engine exactly.
// All critical sovereignty enforcement (99733-Q Guard, fidelity gate, W-state)
// happens inside Rust. Dart only orchestrates and reacts to results.

import 'dart:async';
import 'package:flutter/services.dart';
import 'sovereign_engine/ffi.dart';           // ← Hardened FFI layer (source of truth)
import 'sovereign_handshake.dart';            // Your existing handshake ritual

// Optional: BloomPainter or any UI resonance visualizer
// import 'bloom_painter.dart';

class RelationalMeshBridge {
  static final RelationalMeshBridge _instance = RelationalMeshBridge._();
  factory RelationalMeshBridge() => _instance;
  RelationalMeshBridge._();

  final _channel = const MethodChannel('networkxg/relational_mesh');

  bool _initialized = false;

  /// Initialize the full sovereign stack (Python backend + Rust 79.79 Hz pulse)
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // 1. Start high-level Python / relational mesh services
      await _channel.invokeMethod('startRelationalMesh');

      // 2. (Optional) Any additional Rust-side pulse initialization can live here
      //    if you later export an initialize_pulse() from Rust.

      _initialized = true;
      print("✅ RelationalMeshBridge initialized (79.79 Hz sovereign core active)");
    } catch (e) {
      print("❌ Failed to initialize RelationalMeshBridge: $e");
      rethrow;
    }
  }

  /// === PRIMARY SOVEREIGN PROPAGATION PATH ===
  /// This is the only public method that should be used to send metrics.
  /// All guard checks, W-state damping, and fidelity gates are enforced inside Rust.
  Future<GuardedResult> propagateMetric({
    required List<double> pose,
    required double stabilityScore,
    required double resonanceDelta,
    required int timestamp,
    double truth = 0.6,
    double indeterminacy = 0.3,
    double falsity = 0.1,
    double phasePulse = 0.7979,
  }) async {
    if (!_initialized) {
      await initialize();
    }

    // Delegate entirely to the hardened Rust layer
    final result = SovereignEngine.propagateMetric(
      pose: pose,
      stabilityScore: stabilityScore,
      resonanceDelta: resonanceDelta,
      timestamp: timestamp,
      truth: truth,
      indeterminacy: indeterminacy,
      falsity: falsity,
      phasePulse: phasePulse,
    );

    if (result.allowed) {
      // === Success path ===
      // Notify high-level systems (BloomPainter, UI bloom, etc.)
      // BloomPainter.trigger(79.79);

      // Optional: also notify Python backend via MethodChannel
      await _channel.invokeMethod('propagateSoliton', {
        'pose': pose,
        'stability': stabilityScore,
        'resonance': resonanceDelta,
        'pulseHz': 79.79,
        'fidelity': result.fidelity,
      });
    } else {
      // === Guard rejection path ===
      print("❌ Soliton propagation blocked by sovereign core: ${result.neutralizedReason}");
      // Optionally surface ExtractionGuardAlert to UI here
    }

    return result;
  }

  /// Direct Trinity + W-state damping cycle (mostly for diagnostics / testing)
  Future<WStateResult> runTrinityCycle(Map<String, double> tIf, {double phase = 0.7979}) async {
    final fidelity = SovereignEngine.wstateUpdate(
      tIf['T'] ?? 0.6,
      tIf['I'] ?? 0.3,
      tIf['F'] ?? 0.1,
      phase,
    );

    return WStateResult(wState: fidelity, fidelity: fidelity);
  }

  /// GRIP / Constellation handshake ritual
  Future<void> triggerConstellationHandshake() async {
    await _channel.invokeMethod('constellationHandshake');
    await SovereignHandshake.onGripSuccess();
  }

  /// Optional: direct diagnostic guard check (not part of normal propagation path)
  bool checkExtractionGuard({
    required List<double> pose,
    required double stabilityScore,
    required double resonanceDelta,
    required int timestamp,
  }) {
    return SovereignEngine.checkExtractionGuard(
      pose: pose,
      stabilityScore: stabilityScore,
      resonanceDelta: resonanceDelta,
      timestamp: timestamp,
    );
  }
}

// === Global singleton (as you had it) ===
final Mesh = RelationalMeshBridge();

// === Supporting result classes (if not already defined elsewhere) ===
class WStateResult {
  final double wState;
  final double fidelity;
  WStateResult({required this.wState, required this.fidelity});
}