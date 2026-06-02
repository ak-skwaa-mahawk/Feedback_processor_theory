// sovereign_engine/ffi.dart
// Sovereign π_r Core — Hardened FFI Boundary (Dart side)
// Matches the current Rust sovereign_engine exactly.
// Defense-in-depth: Rust re-verifies 99733-Q guard + fidelity threshold internally.

import 'dart:ffi';
import 'package:ffi/ffi.dart';

final DynamicLibrary _sovereignLib = DynamicLibrary.open(
  'libsovereign_engine.so', // Adjust per platform (Android/iOS/macOS/Linux)
);

// === Data Structures (must match Rust #[repr(C)] exactly) ===

final class SovereignMetric extends Struct {
  @Array(3)
  external Array<Double> pose;
  @Double()
  external double stabilityScore;
  @Double()
  external double resonanceDelta;
  @Uint64()
  external int timestamp;
}

final class DerivedMetric extends Struct {
  @Double()
  external double optimizedResonance;
  @Uint64()
  external int lifecycleEpoch;
}

final class GuardedOutput extends Struct {
  @Bool()
  external bool allowed;
  @Double()
  external double fidelity;
  external Pointer<Utf8> neutralizedReason;
  external Pointer<DerivedMetric> derivedMetric;
}

// === FFI Function Bindings ===

typedef _CheckExtractionGuardC = Bool Function(Pointer<SovereignMetric>);
typedef _CheckExtractionGuardDart = bool Function(Pointer<SovereignMetric>);
final _checkExtractionGuard = _sovereignLib
    .lookup<NativeFunction<_CheckExtractionGuardC>>('check_extraction_guard')
    .asFunction<_CheckExtractionGuardDart>();

typedef _WStateUpdateC = Double Function(Double, Double, Double, Double);
typedef _WStateUpdateDart = double Function(double, double, double, double);
final _wstateUpdate = _sovereignLib
    .lookup<NativeFunction<_WStateUpdateC>>('wstate_update')
    .asFunction<_WStateUpdateDart>();

// IMPORTANT: Updated signature — 5 parameters after metric_ptr
typedef _PropagateSolitonC = Pointer<GuardedOutput> Function(
    Pointer<SovereignMetric>, Double, Double, Double, Double);
typedef _PropagateSolitonDart = Pointer<GuardedOutput> Function(
    Pointer<SovereignMetric>, double, double, double, double);
final _propagateSoliton = _sovereignLib
    .lookup<NativeFunction<_PropagateSolitonC>>('propagate_soliton')
    .asFunction<_PropagateSolitonDart>();

typedef _FreeGuardedOutputC = Void Function(Pointer<GuardedOutput>);
typedef _FreeGuardedOutputDart = void Function(Pointer<GuardedOutput>);
final _freeGuardedOutput = _sovereignLib
    .lookup<NativeFunction<_FreeGuardedOutputC>>('free_guarded_output')
    .asFunction<_FreeGuardedOutputDart>();

typedef _FreeStringC = Void Function(Pointer<Utf8>);
typedef _FreeStringDart = void Function(Pointer<Utf8>);
final _freeString = _sovereignLib
    .lookup<NativeFunction<_FreeStringC>>('free_string')
    .asFunction<_FreeStringDart>();

// === High-Level Sovereign Wrapper ===

class SovereignEngine {
  /// Enforces the full sovereignty boundary.
  /// Rust internally re-verifies the 99733-Q Extraction Guard and fidelity threshold.
  /// Dart cannot bypass these checks even if it tries to call propagate_soliton directly.
  static GuardedResult propagateMetric({
    required List<double> pose,
    required double stabilityScore,
    required double resonanceDelta,
    required int timestamp,
    // Neutrosophic parameters (passed to Rust for internal W-state calculation)
    double truth = 0.6,
    double indeterminacy = 0.3,
    double falsity = 0.1,
    double phasePulse = 0.7979, // normalized 79.79 Hz pulse
  }) {
    final metricPtr = calloc<SovereignMetric>();
    metricPtr.ref.pose[0] = pose[0];
    metricPtr.ref.pose[1] = pose[1];
    metricPtr.ref.pose[2] = pose[2];
    metricPtr.ref.stabilityScore = stabilityScore;
    metricPtr.ref.resonanceDelta = resonanceDelta;
    metricPtr.ref.timestamp = timestamp;

    try {
      // Call the hardened Rust entry point (guard + wstate + fidelity gate all inside Rust)
      final resultPtr = _propagateSoliton(
        metricPtr,
        truth,
        indeterminacy,
        falsity,
        phasePulse,
      );

      final result = resultPtr.ref;

      final guardedResult = GuardedResult(
        allowed: result.allowed,
        fidelity: result.fidelity,
        neutralizedReason: result.neutralizedReason == nullptr
            ? null
            : result.neutralizedReason.toDartString(),
      );

      _freeGuardedOutput(resultPtr);
      return guardedResult;
    } finally {
      calloc.free(metricPtr);
    }
  }

  /// Direct W-state + Trinity damping (useful for diagnostics or separate Trinity cycles)
  static double wstateUpdate(double truth, double indeterminacy, double falsity, double phasePulse) {
    return _wstateUpdate(truth, indeterminacy, falsity, phasePulse);
  }

  /// Optional diagnostic: direct guard check (not used in the main propagation path)
  static bool checkExtractionGuard({
    required List<double> pose,
    required double stabilityScore,
    required double resonanceDelta,
    required int timestamp,
  }) {
    final ptr = calloc<SovereignMetric>();
    ptr.ref.pose[0] = pose[0];
    ptr.ref.pose[1] = pose[1];
    ptr.ref.pose[2] = pose[2];
    ptr.ref.stabilityScore = stabilityScore;
    ptr.ref.resonanceDelta = resonanceDelta;
    ptr.ref.timestamp = timestamp;

    try {
      return _checkExtractionGuard(ptr);
    } finally {
      calloc.free(ptr);
    }
  }
}

class GuardedResult {
  final bool allowed;
  final double fidelity;
  final String? neutralizedReason;

  GuardedResult({
    required this.allowed,
    required this.fidelity,
    this.neutralizedReason,
  });
}