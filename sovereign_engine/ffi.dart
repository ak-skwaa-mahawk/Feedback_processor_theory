// sovereign_engine/ffi.dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

final DynamicLibrary _sovereignLib = DynamicLibrary.open('libsovereign_engine.so'); // Adjust path as needed

// === Data Structures (must match Rust exactly) ===

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

typedef _PropagateSolitonC = Pointer<GuardedOutput> Function(Pointer<SovereignMetric>, Double);
typedef _PropagateSolitonDart = Pointer<GuardedOutput> Function(Pointer<SovereignMetric>, double);

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

// === High-Level Safe Wrapper ===

class SovereignEngine {
  /// Enforces the full sovereignty boundary in the correct order.
  static GuardedResult propagateMetric({
    required List<double> pose,
    required double stabilityScore,
    required double resonanceDelta,
    required int timestamp,
  }) {
    final metricPtr = calloc<SovereignMetric>();
    metricPtr.ref.pose[0] = pose[0];
    metricPtr.ref.pose[1] = pose[1];
    metricPtr.ref.pose[2] = pose[2];
    metricPtr.ref.stabilityScore = stabilityScore;
    metricPtr.ref.resonanceDelta = resonanceDelta;
    metricPtr.ref.timestamp = timestamp;

    try {
      // Step 1: Extraction Guard (99733-Q)
      if (!_checkExtractionGuard(metricPtr)) {
        return GuardedResult(
          allowed: false,
          fidelity: 0.0,
          neutralizedReason: '99733-Q Extraction Guard triggered',
        );
      }

      // Step 2: W-state + Trinity damping
      final fidelity = _wstateUpdate(0.6, 0.3, 0.1, 79.79 * 0.01);

      if (fidelity < 0.9999) {
        return GuardedResult(
          allowed: false,
          fidelity: fidelity,
          neutralizedReason: 'W-state fidelity below 0.9999 threshold',
        );
      }

      // Step 3: Guarded soliton propagation (Rust re-verifies guard internally)
      final resultPtr = _propagateSoliton(metricPtr, fidelity);
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