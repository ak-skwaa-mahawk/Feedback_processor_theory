// sovereign_engine/src/ffi.rs
// Hardened FFI layer for relational_mesh_bridge.dart (AGŁG v89+)

use crate::frame_energy::{EraFrameId, SovereignState, ProjectedState, CriticFeedback, FrameEnergy};
use crate::sovereign_engine::SovereignEngine; // your main engine

use std::sync::Mutex;
use once_cell::sync::Lazy;

static SOVEREIGN_ENGINE: Lazy<Mutex<SovereignEngine>> = Lazy::new(|| {
    Mutex::new(SovereignEngine::new())
});

static FRAME_ENERGY: Lazy<Mutex<FrameEnergy>> = Lazy::new(|| {
    Mutex::new(FrameEnergy::new(SovereignState::default_floor_anchor()))
});

// === Existing hardened exports (matching your Dart bridge) ===

#[no_mangle]
pub extern "C" fn propagate_metric(
    pose: *const f64,
    pose_len: usize,
    stability_score: f64,
    resonance_delta: f64,
    timestamp: u64,
    truth: f64,
    indeterminacy: f64,
    falsity: f64,
    phase_pulse: f64,
) -> GuardedResultFFI {
    // ... existing implementation that runs Extraction Guard + W-state + 79.79 Hz pulse
    // Returns GuardedResultFFI { allowed, fidelity, neutralized_reason }
}

#[no_mangle]
pub extern "C" fn wstate_update(t: f64, i: f64, f: f64, phase: f64) -> f64 {
    // Your existing Trinity damping + normalization logic
    // Returns fidelity
}

#[no_mangle]
pub extern "C" fn check_extraction_guard(
    pose: *const f64,
    pose_len: usize,
    stability_score: f64,
    resonance_delta: f64,
    timestamp: u64,
) -> bool {
    // Direct guard check without full propagation
}

// === NEW: TCP + Frame Energy exports ===

#[no_mangle]
pub extern "C" fn select_frame() -> i32 {
    let mut engine = SOVEREIGN_ENGINE.lock().unwrap();
    let frame = engine.frame_policy.select_frame(&engine.current_state);
    frame as i32
}

#[no_mangle]
pub extern "C" fn propagate_metric_with_frame(
    pose: *const f64,
    pose_len: usize,
    stability_score: f64,
    resonance_delta: f64,
    timestamp: u64,
    frame_id: i32,
) -> GuardedResultWithEnergyFFI {
    let frame = unsafe { std::mem::transmute::<i32, EraFrameId>(frame_id) };
    
    let mut engine = SOVEREIGN_ENGINE.lock().unwrap();
    let frame_energy = FRAME_ENERGY.lock().unwrap();

    // Project state using TCP
    let projected = engine.tcp.project(frame, &engine.current_state);

    // Run guarded propagation
    let guarded = engine.propagate_with_frame(frame, &projected);

    // Compute frame energy
    let energy = frame_energy.compute(frame, &engine.current_state, &projected);

    GuardedResultWithEnergyFFI {
        allowed: guarded.allowed,
        fidelity: guarded.fidelity,
        frame_energy: energy,
        neutralized_reason: guarded.neutralized_reason,
    }
}

#[no_mangle]
pub extern "C" fn run_pwc_tcp_cycle(
    t: f64,
    i: f64,
    f: f64,
    current_frame: i32,
) -> CriticFeedbackFFI {
    let frame = unsafe { std::mem::transmute::<i32, EraFrameId>(current_frame) };
    let mut engine = SOVEREIGN_ENGINE.lock().unwrap();
    let frame_energy = FRAME_ENERGY.lock().unwrap();

    // Run full PWC + TCP cycle
    let feedback = engine.run_cognitive_cycle(frame, t, i, f, &frame_energy);

    CriticFeedbackFFI::from(feedback)
}

// === Supporting FFI result structs ===

#[repr(C)]
pub struct GuardedResultWithEnergyFFI {
    pub allowed: bool,
    pub fidelity: f64,
    pub frame_energy: f64,
    pub neutralized_reason: *const libc::c_char,
}

#[repr(C)]
pub struct CriticFeedbackFFI {
    pub task_reward: f64,
    pub frame_fitness: f64,
    pub frame_energy: f64,
    pub recommended_frame: i32,
}