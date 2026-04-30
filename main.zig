const std = @import("std");

const H: f64 = 3.07;
const FLOOR_COLLAPSE: f64 = 0.073;   // Gwich’in chanchyah/dach’anchyah
const NAVAJO_BOOST: f64 = 0.031;     // Diné niʼ / nahasdzáán
const MAX_K: usize = 5000;           // easily lowered for tiny MCUs

inline fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = @log(k);
    return k * ln_k - k + 0.5 * @log(2.0 * std.math.pi * k);
}

pub fn practical_catch_floor_embedded(signal: []const u8) f64 {
    const n = signal.len + 1;
    const max_k = @min(n, MAX_K);

    var pi_n: f64 = std.math.pi;
    var prev_ln_fact: f64 = 0.0; // incremental cache

    @setEvalBranchQuota(10000); // for comptime safety on small targets

    var k: usize = 1;
    while (k <= max_k) : (k += 1) {
        const kf = @as(f64, @floatFromInt(k));

        // Incremental Stirling
        prev_ln_fact = stirling_lngamma(kf + 1.0);

        // Gwich’in Floor + Navajo anchor
        const floor_val = prev_ln_fact * (1.0 + FLOOR_COLLAPSE);
        const navajo_val = prev_ln_fact * (1.0 + NAVAJO_BOOST);

        const delta = H * (prev_ln_fact + @log(floor_val) + @log(navajo_val)) / (kf * kf);

        pi_n = @mod(pi_n + delta, 2.0 * std.math.pi);
    }
    return pi_n;
}

// ── Bare-metal entry point (replace with UART/LED output on your MCU) ──
pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";

    const pi_r = practical_catch_floor_embedded(test_signal);

    // Example output (replace with hardware console)
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Embedded Zig Floor π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Optimized embedded Floor integration complete.\n", .{});
}