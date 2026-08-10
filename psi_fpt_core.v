// psi_fpt_core.v
module psi_fpt_core (
    input clk_100mhz,
    input rst_n,
    input [15:0] sensor_scrape,
    input [15:0] motor_command,
    input sensor_valid,
    output [15:0] motor_correction,
    output veto_out,
    output [1:0] attention_level
);
    wire [15:0] ref_glyph, error_raw, correction;
    wire error_valid, ern_pulse;
    wire [7:0] theta_power;

    // 1. Reafference
    reafference_comparator u_reaff (
        .clk(clk_100mhz), .rst_n(rst_n),
        .scrape(sensor_scrape),
        .ref_glyph(motor_command),
        .error_raw(error_raw),
        .error_valid(error_valid)
    );

    // 2. ERN
    ern_detector u_ern (
        .clk(clk_100mhz), .rst_n(rst_n),
        .error_raw(error_raw), .error_valid(error_valid),
        .ern_pulse(ern_pulse), .theta_power(theta_power)
    );

    // 3. PID
    pid_controller u_pid (
        .clk(clk_100mhz), .rst_n(rst_n),
        .error(error_raw), .error_valid(error_valid),
        .correction(correction)
    );

    // 4. FIT Attention
    fit_attention_shift u_fit (
        .clk(clk_100mhz), .rst_n(rst_n),
        .ern_pulse(ern_pulse),
        .performance_score(8'd85),  // From task eval
        .attention_level(attention_level)
    );

    // 5. QGH Veto
    qgh_resonance u_qgh (
        .clk(clk_100mhz), .rst_n(rst_n),
        .glyph_in(sensor_scrape),  // Mock
        .ref_glyph(motor_command),
        .glyph_valid(sensor_valid),
        .veto(veto_out)
    );

    assign motor_correction = veto_out ? 16'h0000 : correction;
endmodule