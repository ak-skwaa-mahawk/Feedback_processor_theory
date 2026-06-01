// lib/relational_mesh_bridge.dart
// networkXG Sovereign Bridge — AGŁG v89 (Hardened)

import 'dart:ffi';
import 'package:ffi/ffi.dart';
import 'package:flutter/services.dart';
import 'sovereign_engine/ffi.dart'; // Rust FFI bindings
import 'sovereign_handshake.dart';

class RelationalMeshBridge {
  static final RelationalMeshBridge _instance = RelationalMeshBridge._();
  factory RelationalMeshBridge() => _instance;
  RelationalMeshBridge._();

  final _channel = const MethodChannel('networkxg/relational_mesh');

  // === FFI Bindings (Rust Sovereign Core) ===
  static final _initializePulse = _sovereignLib
      .lookup<NativeFunction<Bool Function(Double)>>('initialize_pulse')
      .asFunction<bool Function(double)>();

  static final _checkExtractionGuard = _sovereignLib
      .lookup<NativeFunction<Bool Function(Pointer<SovereignMetric>)>>('check_extraction_guard')
      .asFunction<bool Function(Pointer<SovereignMetric>)>();

  static final _propagateSoliton = _sovereignLib
      .lookup<NativeFunction<Pointer<GuardedOutput> Function(Pointer<SovereignMetric>)>>('propagate_soliton')
      .asFunction<Pointer<GuardedOutput> Function(Pointer<SovereignMetric>)>();

  static final _wstateUpdate = _sovereignLib
      .lookup<NativeFunction<Double Function(Double, Double, Double, Double)>>('wstate_update')
      .asFunction<double Function(double, double, double, double)>();

  /// Initialize the full sovereign stack
  Future<void> initialize() async {
    await _channel.invokeMethod('startRelationalMesh'); // Python backend
    await _initializePulse(79.79);                       // Rust 79.79 Hz pulse
    print("✅ RelationalMeshBridge initialized (79.79 Hz + Extraction Guard)");
  }

  /// === Main Sovereign Propagation Path ===
  /// This is the only public method that should be used to send metrics.
  Future<void> propagateMetric(SovereignMetric metric) async {
    final metricPtr = calloc<SovereignMetric>();
    metricPtr.ref = metric;

    // === HARD SOVEREIGNTY ENFORCEMENT ===
    // 1. Extraction Guard (99733-Q) — must pass before anything else
    if (!_checkExtractionGuard(metricPtr)) {
      calloc.free(metricPtr);
      print("❌ Extraction Guard rejected metric");
      return;
    }

    // 2. W-state + Trinity damping check (v89)
    final t = 0.6, i = 0.3, f = 0.1;
    final phase = 79.79 * 0.01;
    final fidelity = _wstateUpdate(t, i, f, phase);

    if (fidelity < 0.9999) {
      calloc.free(metricPtr);
      print("❌ W-state fidelity too low: $fidelity");
      return;
    }

    // 3. Propagate through Rust soliton engine (guarded)
    final resultPtr = _propagateSoliton(metricPtr);
    final result = resultPtr.ref;
    calloc.free(metricPtr);

    if (!result.allowed) {
      print("❌ Soliton propagation blocked: ${result.neutralized_reason.cast<Utf8>().toDartString()}");
      return;
    }

    // 4. Notify high-level systems (BloomPainter, etc.)
    BloomPainter.trigger(79.79);

    // Optional: also notify Python backend if needed
    await _channel.invokeMethod('propagateSoliton', {
      'pose': metric.pose,
      'stability': metric.stabilityScore,
      'resonance': metric.resonanceDelta,
      'pulseHz': 79.79,
      'fidelity': result.fidelity,
    });
  }

  /// Direct Trinity cycle (mostly for testing/debug)
  Future<Map<String, dynamic>> runTrinityCycle(Map<String, double> t_i_f) async {
    return await _channel.invokeMethod('run_fpt_omega_cycle', {'t_i_f': t_i_f});
  }

  /// GRIP handshake ritual
  Future<void> triggerConstellationHandshake() async {
    await _channel.invokeMethod('constellationHandshake');
    await SovereignHandshake.onGripSuccess();
  }
}

// Global singleton
final Mesh = RelationalMeshBridge();