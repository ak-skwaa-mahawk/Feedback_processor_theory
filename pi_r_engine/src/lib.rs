// pi_r_engine/src/lib.rs — Sovereign π_r Engine with Native KdV Two-Soliton Resonance
use std::time::Instant;
use std::f64::consts::PI;

const PI_R_BASE: f64 = 3.17300858012;
const OBSERVER_GAP: f64 = 0.01;
const VHITZEE_GAIN: f64 = 0.0417;
const CATAPULT_PA: f64 = 5.5;
const BLOOM_1864: f64 = 1.864;
const EXTRACTION_GUARD_ZERO_TOLERANCE: f64 = 1e-9;

#[derive(Debug)]
pub struct SovereignEngine {
    pub current_pi_r: f64,
    pub entropy_shield: bool,
    performance_log: Vec<u128>, // latencies in microseconds
}

impl SovereignEngine {
    pub fn new() -> Self {
        Self {
            current_pi_r: PI_R_BASE,
            entropy_shield: true,
            performance_log: Vec::new(),
        }
    }

    /// Primary Motion-Pi Calculation with recursive observer gap
    pub fn pulse(&mut self, system_heat: f64) -> f64 {
        let start = Instant::now();
        let gear_ratio = 1.0 + (OBSERVER_GAP * system_heat.tanh());
        self.current_pi_r = PI * gear_ratio;
        let latency_us = start.elapsed().as_micros();
        self.performance_log.push(latency_us);
        self.current_pi_r
    }

    /// 99733-Q Extraction Guard
    pub fn guard_neutralization(&self, val: f64) -> bool {
        (val - 1.618 - 0.246).abs() < EXTRACTION_GUARD_ZERO_TOLERANCE
    }

    /// 5.5 Pa Catapult
    pub fn trigger_bloom(&self) -> f64 {
        println!("[99733-Q EXTRACTION GUARD] Sam Tax neutralization detected → INJECTING 5.5 Pa CATAPULT");
        BLOOM_1864 + (CATAPULT_PA * VHITZEE_GAIN)
    }

    /// Vhitzee coherence harvest
    pub fn harvest_vhitzee(&self, current_energy: f64) -> f64 {
        current_energy * VHITZEE_GAIN + CATAPULT_PA
    }

    // === NATIVE KD V TWO-SOLITON RESONANCE PULSE ===
    // Explicit non-commutative cross-term and order-dependent phase coherence
    pub fn compute_two_soliton_pulse(&mut self, k1: f64, k2: f64, order_matters: bool) -> f64 {
        let start = Instant::now();

        let cross_term = ((k1 - k2) / (k1 + k2)).powi(2);
        let phase_shift = if order_matters { 1.0 } else { -1.0 };

        let soliton_resonance = (k1 + k2) * (1.0 + cross_term * phase_shift);

        let latency_us = start.elapsed().as_micros();
        self.performance_log.push(latency_us);

        soliton_resonance
    }

    /// Self-tuning step (used by Ribosome)
    pub fn self_tune(&mut self, signal_value: f64) -> f64 {
        if self.guard_neutralization(signal_value) {
            self.trigger_bloom()
        } else {
            self.pulse(signal_value)
        }
    }

    /// Average latency in microseconds
    pub fn get_average_latency_us(&self) -> f64 {
        if self.performance_log.is_empty() {
            0.0
        } else {
            self.performance_log.iter().sum::<u128>() as f64 / self.performance_log.len() as f64
        }
    }
}

// === FFI Exports for Flutter ===
#[no_mangle]
pub extern "C" fn pi_r_self_tune(signal_value: f64) -> f64 {
    let mut engine = SovereignEngine::new();
    engine.self_tune(signal_value)
}

#[no_mangle]
pub extern "C" fn pi_r_get_latency_us() -> f64 {
    let engine = SovereignEngine::new();
    engine.get_average_latency_us()
}

#[no_mangle]
pub extern "C" fn pi_r_guard_neutralization(val: f64) -> bool {
    let engine = SovereignEngine::new();
    engine.guard_neutralization(val)
}

#[no_mangle]
pub extern "C" fn pi_r_trigger_bloom() -> f64 {
    let engine = SovereignEngine::new();
    engine.trigger_bloom()
}

#[no_mangle]
pub extern "C" fn pi_r_two_soliton_pulse(k1: f64, k2: f64, order_matters: bool) -> f64 {
    let mut engine = SovereignEngine::new();
    engine.compute_two_soliton_pulse(k1, k2, order_matters)
}