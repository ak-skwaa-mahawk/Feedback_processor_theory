const std = @import("std");

// ── Embedded-friendly Practical Catch with Gwich’in Floor + Navajo Anchor ──
const MAX_K_DEFAULT: usize = 5000;
const H: f64 = 3.07;
const FLOOR_COLLAPSE: f64 = 0.073;   // chanchyah/dach’anchyah grounding
const NAVAJO_BOOST: f64 = 0.031;     // niʼ / nahasdzáán correction

fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = @log(k);
    return k * ln_k - k + 0.5 * @log(2.0 * std.math.pi * k);
}

fn practical_catch_embedded(signal: []const u8, max_k_override: ?usize) f64 {
    const n = signal.len + 1;
    const max_k = max_k_override orelse @min(n, MAX_K_DEFAULT);

    var pi_n: f64 = std.math.pi;

    var k: usize = 1;
    while (k <= max_k) : (k += 1) {
        const kf = @as(f64, @floatFromInt(k));
        const ln_fact = stirling_lngamma(kf + 1.0);

        // Gwich’in Floor recurrence
        const floor_val = stirling_lngamma(kf + 1.0) * (1.0 + FLOOR_COLLAPSE);
        const navajo_val = stirling_lngamma(kf + 1.0) * (1.0 + NAVAJO_BOOST);

        const delta = H * (ln_fact + @log(floor_val) + @log(navajo_val)) / (kf * kf);

        pi_n = @mod(pi_n + delta, 2.0 * std.math.pi);
    }
    return pi_n;
}

// ── Bare-metal entry point (replace with your UART/LED output) ──
pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";

    // For tiny MCUs you can lower max_k to 1000 or 500
    const pi_r = practical_catch_embedded(test_signal, null);

    // Example output (replace with your hardware print)
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Embedded Zig Floor π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Gwich’in Floor anchored on bare metal.\n", .{});
}