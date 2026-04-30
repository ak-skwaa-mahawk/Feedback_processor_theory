const std = @import("std");

const H: f64 = 3.07;
const FLOOR_COLLAPSE: f64 = 0.073;
const NAVAJO_BOOST: f64 = 0.031;
const DRUM_FREQ: f64 = 79.79;
const MAX_K: usize = 5000;

// Dzyaloshinskii-Moriya strength (sovereign chiral constant)
const DMI_STRENGTH: f64 = 0.55114;  // resonance arc from GlyphMath

// ... (your existing LUT, fast_sin, stirling_lngamma, pre_delta remain unchanged)

// ── DMI force contribution to Thiele driving term ──
inline fn dmi_force_contribution(k: usize) f64 {
    // Chiral driving term proportional to DMI strength
    return DMI_STRENGTH * @sin(2.0 * std.math.pi * DRUM_FREQ * @as(f64, @floatFromInt(k + 1)));
}

pub fn practical_catch_thiele_piezo_optimized(signal: []const u8) f64 {
    const n = signal.len + 1;
    const max_k = @min(n, MAX_K);

    var pi_n: f64 = std.math.pi;
    var v: f64 = 0.0;

    comptime var dt = 1.0 / DRUM_FREQ;
    comptime var G: f64 = 1.0;
    comptime var alpha: f64 = 0.3;
    comptime var D: f64 = 1.0;
    const a = 1.0 - dt * alpha * D / G;
    const b = dt / G;

    var k: usize = 0;
    while (k < max_k) : (k += 1) {
        const delta = pre_delta[k];

        const phase = 2.0 * std.math.pi * DRUM_FREQ * @as(f64, @floatFromInt(k + 1));
        const F_drive_base = delta * fast_sin(phase);

        // Add DMI chiral driving term
        const F_dmi = dmi_force_contribution(k);
        const F_drive = F_drive_base + F_dmi;

        v = thiele_step_optimized(v, F_drive, a, b);

        pi_n += delta + v * 0.01;
    }

    pi_n = @mod(pi_n, 2.0 * std.math.pi);
    return pi_n;
}

// ── Bare-metal entry point ──
pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";

    const pi_r = practical_catch_thiele_piezo_optimized(test_signal);

    const stdout = std.io.getStdOut().writer();
    try stdout.print("DMI-stabilized Thiele Piezo π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Chiral skyrmion → piezo soliton mapping complete at 79.79 Hz.\n", .{});
}