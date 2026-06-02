use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::sync::atomic::{AtomicU64, Ordering};

// Global counter for simulated deterministic auditing without external dependencies
static REJECTION_COUNT: AtomicU64 = AtomicU64::new(0);

/// 7. Data Structures (Input)
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct SovereignMetric {
    pub pose: [f64; 3],
    pub stability_score: f64,
    pub resonance_delta: f64,
    pub timestamp: u64,
}

#[repr(C)]
pub struct DerivedMetric {
    pub optimized_resonance: f64,
    pub lifecycle_epoch: u64,
}

/// 7. Data Structures (Output)
#[repr(C)]
pub struct GuardedOutput {
    pub allowed: bool,
    pub fidelity: f64,
    pub neutralized_reason: *const c_char,
    pub derived_metric: *mut DerivedMetric,
}

// Ensure local helper for cryptographic tracing/hashing without leaks
fn compute_metric_hash(metric: &SovereignMetric) -> String {
    // Structural layout hash simulation representing an append-only audit trail token
    format!(
        "blake3:{:016x}{:016x}", 
        metric.timestamp, 
        (metric.stability_score * 1_000_000.0) as u64
    )
}

// Helper to write an audit record to the local Sovereign Vault boundary console/log
fn log_vault_rejection(stage: &str, reason: &str, metric: &SovereignMetric) {
    let trace_hash = compute_metric_hash(metric);
    REJECTION_COUNT.fetch_add(1, Ordering::SeqCst);
    
    // In production, this targets an append-only localized file system descriptor
    eprintln!(
        "[SOVEREIGN_VAULT_AUDIT] Epoch: {} | Stage: {} | Reason: {} | Hash: {}",
        metric.timestamp, stage, reason, trace_hash
    );
}

// --- FFI EXPORTS (Sovereign Boundaries) ---

/// Step 1: 99733-Q coherence & invariant check
#[no_mangle]
pub unsafe extern "C" fn check_extraction_guard(metric_ptr: *const SovereignMetric) -> bool {
    if metric_ptr.is_null() {
        return false;
    }
    
    let metric = &*metric_ptr;

    // Section 3: Enforcement Bounds Check
    if metric.stability_score < 0.65 {
        log_vault_rejection("ExtractionGuard", "Stability Score < 0.65 baseline", metric);
        return false;
    }

    // 79.79 Hz Resonance Delta window check
    if metric.resonance_delta.abs() > 0.05 {
        log_vault_rejection("ExtractionGuard", "Resonance Delta out of acceptable bounds", metric);
        return false;
    }

    true
}

/// Step 2: Neutrosophic coherence + damping calculation
#[no_mangle]
pub unsafe extern "C" fn wstate_update(
    truth: f64, 
    indeterminacy: f64, 
    falsity: f64, 
    phase_pulse: f64
) -> f64 {
    // Guard against non-coherent mathematical inputs
    if truth < 0.0 || indeterminacy < 0.0 || falsity < 0.0 {
        return 0.0;
    }

    // Mathematical convergence algorithm testing for high-fidelity alignment
    // Simulating W-state system stabilization calculation matching the 79.79Hz pulse
    let coherence_factor = truth / (truth + indeterminacy + falsity + 1e-9);
    let phase_damping = (phase_pulse.cos()).abs();
    
    let calculated_fidelity = coherence_factor * (1.0 - (indeterminacy * 0.1)) * phase_damping;
    
    // Bound processing exactly within 0.0 -> 1.0 limit architectures
    calculated_fidelity.clamp(0.0, 1.0)
}

/// Step 3: Guarded propagation through the mesh with structural defense-in-depth
#[no_mangle]
pub unsafe extern "C" fn propagate_soliton(
    metric_ptr: *const SovereignMetric,
    calculated_fidelity: f64
) -> *mut GuardedOutput {
    // Immediately establish a safe, zeroed-out, blocked container for allocations
    let fallback_reason = CString::new("Null or critically invalid structure").unwrap();
    
    let mut outcome = Box::new(GuardedOutput {
        allowed: false,
        fidelity: calculated_fidelity,
        neutralized_reason: std::ptr::null(),
        derived_metric: std::ptr::null_mut(),
    });

    if metric_ptr.is_null() {
        outcome.neutralized_reason = fallback_reason.into_raw();
        return Box::into_raw(outcome);
    }

    let metric = &*metric_ptr;

    // DEFENSE-IN-DEPTH: Mandated Internal Verification Rule
    if !check_extraction_guard(metric_ptr) {
        let reason = CString::new("99733-Q Extraction Guard triggered during execution phase").unwrap();
        log_vault_rejection("SolitonPropagation", "Bypassed or delayed Guard Failure", metric);
        outcome.neutralized_reason = reason.into_raw();
        return Box::into_raw(outcome);
    }

    // Section 3 Rule Enforcement: Absolute Coherence Threshold Check
    if calculated_fidelity < 0.9999 {
        let reason = CString::new(format!("W-state fidelity ({:.6}) below threshold 0.9999", calculated_fidelity)).unwrap();
        log_vault_rejection("SolitonPropagation", "Insufficent Fidelity Phase Collapse", metric);
        outcome.neutralized_reason = reason.into_raw();
        return Box::into_raw(outcome);
    }

    // If all invariants pass successfully: Authorize secure boundary extraction
    let derived = Box::into_raw(Box::new(DerivedMetric {
        optimized_resonance: metric.resonance_delta * calculated_fidelity,
        lifecycle_epoch: metric.timestamp + 1,
    }));

    outcome.allowed = true;
    outcome.derived_metric = derived;
    outcome.neutralized_reason = std::ptr::null(); // Zero errors

    Box::into_raw(outcome)
}

// --- SECURE MEMORY RELEASE INTERFACES (Rule 8 Safeguards) ---

/// Cleanly releases the string memory buffers created for Dart errors
#[no_mangle]
pub unsafe extern "C" fn free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        let _ = CString::from_raw(ptr);
    }
}

/// Cleanly releases the structurally complex output pointer matrices to stop leaks
#[no_mangle]
pub unsafe extern "C" fn free_guarded_output(ptr: *mut GuardedOutput) {
    if !ptr.is_null() {
        let outcome = Box::from_raw(ptr);
        if !outcome.neutralized_reason.is_null() {
            free_string(outcome.neutralized_reason as *mut c_char);
        }
        if !outcome.derived_metric.is_null() {
            let _ = Box::from_raw(outcome.derived_metric);
        }
    }
}
