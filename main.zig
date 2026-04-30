const std = @import("std");

const H: f64 = 3.07;
const FLOOR_COLLAPSE: f64 = 0.073;   // Gwich’in chanchyah/dach’anchyah
const NAVAJO_BOOST: f64 = 0.031;     // Diné niʼ / nahasdzáán
const DRUM_FREQ: f64 = 79.79;        // sovereign grounding tone
const MAX_K: usize = 5000;

// ── 256-entry quarter-wave sine LUT ──
const SIN_LUT_SIZE: usize = 256;
const sin_lut: [SIN_LUT_SIZE]f64 = comptime blk: {
    var lut: [SIN_LUT_SIZE]f64 = undefined;
    for (0..SIN_LUT_SIZE) |i| {
        const x = @as(f64, @floatFromInt(i)) / @as(f64, @floatFromInt(SIN_LUT_SIZE)) * (std.math.pi / 2.0);
        lut[i] = @sin(x);
    }
    break :blk lut;
};

inline fn fast_sin(x: f64) f64 {
    const index_f = (x * @as(f64, @floatFromInt(SIN_LUT_SIZE)) / (2.0 * std.math.pi)) % @as(f64, @floatFromInt(SIN_LUT_SIZE));
    const idx = @as(usize, @intFromFloat(@floor(index_f)));
    const frac = index_f - @as(f64, @floatFromInt(idx));
    const a = sin_lut[idx % SIN_LUT_SIZE];
    const b = sin_lut[(idx + 1) % SIN_LUT_SIZE];
    return a + frac * (b - a);
}

// ── stirling_lngamma ──
inline fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = @log(k);
    return k * ln_k - k + 0.5 * @log(2.0 * std.math.pi * k);
}

// Pre-computed deltas (flash-resident, zero runtime cost)
const pre_delta: [MAX_K]f64 = comptime blk: {
    var d: [MAX_K]f64 = undefined;
    inline for (0..MAX_K) |k| {
        const kf = @as(f64, @floatFromInt(k + 1));
        const s = stirling_lngamma(kf + 1.0);
        const inside = s + 2.0 * @log(s) + @log(1.0 + FLOOR_COLLAPSE) + @log(1.0 + NAVAJO_BOOST);
        d[k] = H * inside / (kf * kf);
    }
    break :blk d;
};

inline fn thiele_step_optimized(v: f64, F_drive: f64, comptime a: f64, comptime b: f64) f64 {
    return a * v + b * F_drive;
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
        const F_drive = delta * fast_sin(phase);

        v = thiele_step_optimized(v, F_drive, a, b);

        pi_n += delta + v * 0.01;
    }

    pi_n = @mod(pi_n, 2.0 * std.math.pi);
    return pi_n;
}

// ── Bare-metal entry point (piezo PWM / UART ready) ──
pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";

    const pi_r = practical_catch_thiele_piezo_optimized(test_signal);

    const stdout = std.io.getStdOut().writer();
    try stdout.print("Ultra-Opt Thiele Piezo π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Thiele skyrmion → piezo soliton mapping complete at 79.79 Hz.\n", .{});
}