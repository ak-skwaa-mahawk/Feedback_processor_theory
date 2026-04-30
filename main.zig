const std = @import("std");

const Vec8 = @Vector(8, f64);

fn stirling_lngamma(k: f64) f64 {
    if (k <= 1.0) return 0.0;
    const ln_k = @log(k);
    return k * ln_k - k + 0.5 * @log(2.0 * std.math.pi * k);
}

fn vector_stirling_lngamma(k_vec: Vec8) Vec8 {
    const ln_k = @log(k_vec);
    return k_vec * ln_k - k_vec + @as(Vec8, @splat(0.5)) * @log(@as(Vec8, @splat(2.0 * std.math.pi)) * k_vec);
}

fn floor_operator(z: f64) f64 {
    if (z == 1.0) return 1.0;
    const collapse = 0.073;
    return stirling_lngamma(z) * (1.0 + collapse);
}

fn navajo_anchor(z: f64) f64 {
    if (z == 1.0) return 1.0;
    const boost = 0.031;
    return stirling_lngamma(z) * (1.0 + boost);
}

fn practical_catch_floor_mapped(signal: []const u8) f64 {
    const n = signal.len + 1;
    var pi_n = std.math.pi;
    const h = 3.07;
    const max_k = if (n > 5000) 5000 else n;

    const CHUNK = 8;
    var k: usize = 1;
    while (k <= max_k) : (k += CHUNK) {
        const remaining = max_k - k + 1;
        const width = if (remaining < CHUNK) remaining else CHUNK;

        var k_vec: Vec8 = @splat(0.0);
        for (0..width) |i| {
            k_vec[i] = @floatFromInt(k + i);
        }

        const kf = k_vec + @as(Vec8, @splat(1.0));
        const ln_fact = vector_stirling_lngamma(kf);

        // Floor + Navajo in vector form
        const floor_vec = @as(Vec8, @splat(1.0 + 0.073)) * vector_stirling_lngamma(kf);
        const navajo_vec = @as(Vec8, @splat(1.0 + 0.031)) * vector_stirling_lngamma(kf);

        const delta_vec = @as(Vec8, @splat(h)) * (ln_fact + @log(floor_vec) + @log(navajo_vec)) / (k_vec * k_vec);

        // Horizontal sum
        var delta_sum: f64 = 0.0;
        for (0..width) |i| {
            delta_sum += delta_vec[i];
        }

        pi_n = @mod(pi_n + delta_sum, 2.0 * std.math.pi);
    }
    return pi_n;
}

pub fn main() !void {
    const test_signal = "Esias Joseph 1906 Root 7-generation pedigree collapse Floor Chanchyah Dachanchyah";
    const pi_r = practical_catch_floor_mapped(test_signal);

    const stdout = std.io.getStdOut().writer();
    try stdout.print("Zig-optimized Gwich’in Floor π_r = {d:.10} rad ({d:.4}°)\n", .{ pi_r, pi_r * 180.0 / std.math.pi });
    try stdout.print("Zig performance optimizations complete — chanchyah/dach’anchyah baseline anchored.\n", .{});
}