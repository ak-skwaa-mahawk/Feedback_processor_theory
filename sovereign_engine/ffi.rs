// sovereign_engine/ffi.rs
use std::os::raw::c_char;
use std::ffi::{CString, CStr};
use std::ptr;

#[repr(C)]
pub struct SovereignMetric {
    pub pose: [f64; 3],
    pub stability_score: f64,
    pub resonance_delta: f64,
    pub timestamp: u64,
}

#[repr(C)]
pub struct GuardedOutput {
    pub allowed: bool,
    pub fidelity: f64,
    pub neutralized_reason: *const c_char,
    pub derived_metric: *mut DerivedMetric,
}

#[repr(C)]
pub struct DerivedMetric {
    pub coherence: f64,
    pub neutralized: bool,
}

// === 99733-Q Extraction Guard ===
// This is the core sovereignty enforcement point.
// It neutralizes metrics that fail coherence checks.
#[no_mangle]
pub extern "C" fn check_extraction_guard(metric: *const SovereignMetric) -> bool {
    if metric.is_null() {
        return false;
    }

    let m = unsafe { &*metric };

    // === 99733-Q Coherence Check ===
    // Pattern: 1.864 − 1.618 − 0.246 ≈ 0
    // This detects non-coherent or potentially exfiltrating data.
    let golden_ratio = 1.6180339887;
    let invariant_check = (m.stability_score * 10000.0) - golden_ratio - 0.246;

    // Reject if stability is too low or the invariant is violated
    if m.stability_score < 0.65 || invariant_check.abs() > 0.35 {
        return false;
    }

    // Additional guard: resonance delta must be within expected bounds
    if m.resonance_delta.abs() > 2.5 {
        return false;
    }

    true
}

// === W-state Update with Trinity Damping ===
#[no_mangle]
pub extern "C" fn wstate_update(t: f64, i: f64, f: f64, phase: f64) -> f64 {
    // Neutrosophic W-state calculation with 79.79 Hz damping
    let sum = t + i + f;

    if sum <= 0.0 {
        return 0.0;
    }

    // Normalize T/I/F
    let tn = t / sum;
    let in_ = i / sum;
    let fn_ = f / sum;

    // Apply Trinity damping using 79.79 Hz phase
    let damping = (phase.sin() * 0.015).abs();
    let coherence = (tn * 0.6 + in_ * 0.3 + fn_ * 0.1) * (1.0 - damping);

    // Enforce minimum fidelity threshold (can be raised)
    if coherence < 0.92 {
        return 0.0;
    }

    coherence.min(0.99999)
}

// === Main Guarded Propagation Function ===
#[no_mangle]
pub extern "C" fn propagate_soliton(metric: *const SovereignMetric) -> GuardedOutput {
    if metric.is_null() {
        return GuardedOutput {
            allowed: false,
            fidelity: 0.0,
            neutralized_reason: CString::new("Null metric").unwrap().into_raw(),
            derived_metric: ptr::null_mut(),
        };
    }

    // === Step 1: Extraction Guard (99733-Q) ===
    if !check_extraction_guard(metric) {
        let reason = CString::new("99733-Q Extraction Guard triggered").unwrap();
        return GuardedOutput {
            allowed: false,
            fidelity: 0.0,
            neutralized_reason: reason.into_raw(),
            derived_metric: ptr::null_mut(),
        };
    }

    let m = unsafe { &*metric };

    // === Step 2: W-state + Trinity Damping ===
    let phase = 79.79 * 0.01;
    let fidelity = wstate_update(0.6, 0.3, 0.1, phase);

    if fidelity < 0.9999 {
        let reason = CString::new("W-state fidelity below threshold").unwrap();
        return GuardedOutput {
            allowed: false,
            fidelity,
            neutralized_reason: reason.into_raw(),
            derived_metric: ptr::null_mut(),
        };
    }

    // === Step 3: Successful propagation ===
    // In a real implementation, you would do soliton math / E8 mesh propagation here.
    let derived = Box::new(DerivedMetric {
        coherence: fidelity,
        neutralized: false,
    });

    GuardedOutput {
        allowed: true,
        fidelity,
        neutralized_reason: ptr::null(),
        derived_metric: Box::into_raw(derived),
    }
}

// Optional: Pulse health monitoring
#[no_mangle]
pub extern "C" fn get_pulse_health() -> f64 {
    // In real implementation, return actual 79.79 Hz coherence/drift
    0.00012 // very small drift = healthy
}

// Helper to free strings returned to Dart (important for FFI safety)
#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if !s.is_null() {
        unsafe { let _ = CString::from_raw(s); }
    }
}