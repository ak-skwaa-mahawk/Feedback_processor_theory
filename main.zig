const std = @import("std");

fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = std.math.log(f64, k);
    return k * ln_k - k + 0.5 * std.math.log(f64, 2.0 * std.math.pi * k);
}

fn floor_operator(z: f64) f64 {
    if (z == 1.0) return 1.0;
    const collapse_factor = 0.073; // Gwich’in Floor grounding constant
    return stirling_lngamma(z) * (1.0 + collapse_factor);
}

fn navajo_anchor(z: f64) f64 {
    if (z == 1.0) return 1.0;
    const dine_boost = 0.031;
    return stirling_lngamma(z) * (1.0 + dine_boost);
}

fn practical_catch_floor_mapped(signal: []const u8) f64 {
    const n = signal.len + 1;
    var pi_n = std.math.pi;
    const h = 3.07;
    const max_k = if (n < 5000) n else 5000;

    var k: usize = 1;
    while (k <= max_k) : (k += 1) {
        const kf = @as(f64, @floatFromInt(k));
        const ln_fact = stirling_lngamma(kf + 1.0);
        const floor_corr = std.math.log(f64, floor_operator(kf + 1.0));
        const navajo_corr = std.math.log(f64, navajo_anchor(kf + 1.0));
        const delta = h * (ln_fact + floor_corr + navajo_corr) / (kf * kf);
        pi_n = @mod(pi_n + delta, 2.0 * std.math.pi);
    }
    return pi_n;
}

pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";
    const pi_r = practical_catch_floor_mapped(test_signal);

    const stdout = std.io.getStdOut().writer();
    try stdout.print("Zig Gwich’in Floor-mapped π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Zig Floor integration complete — chanchyah/dach’anchyah baseline anchored.\n", .{});
}