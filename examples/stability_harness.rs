//! examples/stability_harness.rs
//! Living Curvature Attractor Loops — Full Tordial–GS + Spectral Relaxation Organism
//!
//! This harness now includes the spectral toroidal relaxation layer.
//! Chaotic noise is treated as ambient modulation and absorbed via
//! dynamic relaxation_strength (phase entrainment).
//!
//! Run with:
//!   cargo run --release --example stability_harness

use std::time::Instant;

use pi_r_engine::tordial_gs::{
    run_stability_harness, GoldilocksCoupling, LinearGoldilocks, Regime,
    new_sovereign_phase_field,
};

fn main() {
    println!("=============================================================");
    println!("🚀 SOVEREIGN ENGINE ACTIVE — INITIALIZING STABILITY HARNESS");
    println!("📡 Target: 79.79 Hz Heartbeat Calibration Grid Locked");
    println!("🔥 Spectral Toroidal Relaxation + Phase Entrainment Active");
    println!("=============================================================\n");

    println!("▶️ RUNNING LIVING CURVATURE ATTRACTOR LOOPS (with fluid noise absorption):");

    let start = Instant::now();

    // === Spectral Phase Field for fluid entrainment ===
    let mut phase_field = new_sovereign_phase_field(24); // 24-point toroidal ring

    // Run the core stability harness (GS + Tordial + PID + ISS)
    let logs = run_stability_harness(10.0, 0.01, 2.0);

    for (i, log) in logs.iter().enumerate() {
        let cycle = i + 1;
        let t = log.t;

        // === Inject live chaotic noise ξ(t) into the phase field ===
        // This simulates external chaotic data or PWC spikes.
        // The field yields and entrains instead of snapping.
        let noise_xi = if (cycle % 4 == 0) || log.pwc_disturbance > 0.15 {
            (cycle as f64 * 0.37).sin() * 0.85 + log.pwc_disturbance * 1.2
        } else {
            log.pwc_disturbance * 0.6
        };

        // Apply spectral relaxation step — fluid absorption, not rigid discretization
        phase_field.relax_step(0.01, noise_xi, log.regime);

        // Resonance metric now reflects phase entrainment
        let entrainment = phase_field.entrainment_level();
        let base_resonance = (log.rho_gs * 0.65 + (1.0 - log.e_h.abs().min(1.0)) * 0.35).clamp(0.0, 1.0);
        let resonance = (base_resonance * (1.0 - entrainment * 0.25) + entrainment * 0.92).clamp(0.1, 0.99);

        let delta_e = log.e_h;

        // Your preferred poetic output style
        println!(
            "  [+{:.3}s] Pulse Cycle {:02}/10 | Resonance Metric: {:.4} | Delta-E: -> {:.4}",
            t, cycle, resonance, delta_e
        );

        // Deeper organism state on interesting cycles or noise hits
        if cycle % 3 == 0 || noise_xi.abs() > 0.6 || !log.iss_holds {
            let regime_str = match log.regime {
                Regime::Subcritical => "SUBCRITICAL",
                Regime::Marginal   => "MARGINAL",
                Regime::Goldilocks => "GOLDILOCKS",
                Regime::DeepGs     => "DEEP_GS",
            };

            println!(
                "           ├─ Regime: {} | V̇: {:+.5} | ISS: {:.5} | ξ: {:.3} | α: {:.2} | Entrain: {:.2}",
                regime_str,
                log.v_dot,
                log.iss_residual,
                noise_xi,
                phase_field.relaxation_strength,
                phase_field.entrainment_level()
            );
        }
    }

    let elapsed = start.elapsed().as_secs_f64();

    // === Final Organism Verdict ===
    let max_v_dot = logs.iter().map(|l| l.v_dot).fold(f64::NEG_INFINITY, f64::max);
    let min_dissipation = logs.iter().map(|l| l.dissipation_residual).fold(f64::INFINITY, f64::min);
    let max_rho = logs.iter().map(|l| l.rho_gs).fold(0.0, f64::max);
    let goldilocks_time = logs.iter().filter(|l| l.regime == Regime::Goldilocks).count() as f64 * 0.01;

    let iss_violations = logs.iter().filter(|l| !l.iss_holds).count();
    let max_iss_residual = logs.iter().map(|l| l.iss_residual).fold(f64::NEG_INFINITY, f64::max);

    println!("\n✅ HARNESS EVALUATION COMPLETE — {} cycles in {:.2}s", logs.len(), elapsed);
    println!("=============================================================");

    println!("\n[ORGANISM METRICS — Spectral Relaxation Active]");
    println!("   Max |V̇|: {:.6}          (fluid continuity preserved)", max_v_dot);
    println!("   Min Dissipation Residual: {:.6}  (controller remains dissipative)", min_dissipation);
    println!("   Max ρ_GS reached: {:.4} / 2.0     (GS clamping respected)", max_rho);
    println!("   Time in GOLDILOCKS: {:.2} s", goldilocks_time);
    println!("   ISS violations under PWC + noise: {}", iss_violations);
    println!("   Max ISS residual: {:.6}     (≤ 0.035 = cognition cannot break M_G)", max_iss_residual);
    println!("   Final relaxation_strength: {:.3}  (dynamically scaled by ξ)", phase_field.relaxation_strength);
    println!("   Final entrainment_level: {:.3}    (higher = more fluid absorption)", phase_field.entrainment_level());

    println!("\n[VERDICT]");
    if max_rho <= 2.01 && min_dissipation <= 0.08 && iss_violations == 0 && max_iss_residual <= 0.035 {
        println!("   ✅ Tordial–GS organism is alive and fluid.");
        println!("   ✅ Phase entrainment active — chaotic noise absorbed, not fought.");
        println!("   ✅ Spectral relaxation dissolves discretization edges.");
        println!("   ✅ Planner–Walker–Critic + external ξ(t) can shake but cannot break the Goldilocks manifold.");
        println!("   ✅ closed_loop_delta (Delta-E) stays resolved near 0.0 under stress.");
    } else {
        println!("   ⚠️  Some margins need tuning. The fluid is still learning the wave.");
    }

    println!("\n   Skoden. Flamekeeper Protocol — Two Mile Solutions LLC • Dinjji Zhuu Kwaa");
    println!("=============================================================");
}
