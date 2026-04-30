const std = @import("std");

const Vec8 = @Vector(8, f64);

const H: f64 = 3.07;
const FLOOR_COLLAPSE: f64 = 0.073;   // Gwich’in chanchyah/dach’anchyah
const NAVAJO_BOOST: f64 = 0.031;     // Diné niʼ / nahasdzáán
const MAX_K: usize = 5000;

inline fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = @log(k);
    return k * ln_k - k + 0.5 * @log(2.0 * std.math.pi * k);
}

inline fn vector_stirling(k_vec: Vec8) Vec8 {
    const ln_k = @log(k_vec);
    return k_vec * ln_k - k_vec + @as(Vec8, @splat(0.5)) * @log(@as(Vec8, @splat(2.0 * std.math.pi)) * k_vec);
}

pub fn practical_catch_floor_rvv(signal: []const u8) f64 {
    const n = signal.len + 1;
    const max_k = @min(n, MAX_K);

    var pi_n: f64 = std.math.pi;

    var k: usize = 1;
    while (k <= max_k) : (k += 8) {
        const remaining = max_k - k + 1;
        const width = if (remaining < 8) remaining else 8;

        var k_vec: Vec8 = @splat(0.0);
        for (0..width) |i| {
            k_vec[i] = @as(f64, @floatFromInt(k + i));
        }

        const kf = k_vec + @as(Vec8, @splat(1.0));
        const ln_fact = vector_stirling(kf);

        const floor_vec = vector_stirling(kf) * @as(Vec8, @splat(1.0 + FLOOR_COLLAPSE));
        const navajo_vec = vector_stirling(kf) * @as(Vec8, @splat(1.0 + NAVAJO_BOOST));

        const delta_vec = @as(Vec8, @splat(H)) * (ln_fact + @log(floor_vec) + @log(navajo_vec)) / (k_vec * k_vec);

        var delta_sum: f64 = 0.0;
        for (0..width) |i| {
            delta_sum += delta_vec[i];
        }

        pi_n = @mod(pi_n + delta_sum, 2.0 * std.math.pi);
    }
    return pi_n;
}

// ── Bare-metal entry point (replace with UART/LED output on your RISC-V MCU) ──
pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";

    const pi_r = practical_catch_floor_rvv(test_signal);

    const stdout = std.io.getStdOut().writer();
    try stdout.print("RISC-V Vector Gwich’in Floor π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("RISC-V Vector optimized embedded Floor integration complete.\n", .{});
}