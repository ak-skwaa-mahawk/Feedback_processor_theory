// fpt_virtex5.v — Top module for Virtex-5
`include "psi_fpt_core.v"

module fpt_virtex5 (
    input clk_125mhz,
    input rst_n,
    input [15:0] sensor_scrape,
    input sensor_valid,
    input [15:0] motor_command,
    output [15:0] motor_correction,
    output veto_out,
    output [1:0] attention_level,
    output led_red,
    output led_green
);
    wire clk_250mhz;
    wire dcm_lock;

    // DCM: 125 MHz → 250 MHz
    DCM_SP #(
        .CLKFX_MULTIPLY(2),
        .CLKFX_DIVIDE(1),
        .CLKIN_PERIOD(8.0)
    ) dcm (
        .CLKIN(clk_125mhz),
        .CLKFB(clk_250mhz),
        .RST(~rst_n),
        .CLKFX(clk_250mhz),
        .LOCKED(dcm_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_250mhz),
        .rst_n(rst_n & dcm_lock),
        .sensor_scrape(sensor_scrape),
        .motor_command(motor_command),
        .sensor_valid(sensor_valid),
        .motor_correction(motor_correction),
        .veto_out(veto_out),
        .attention_level(attention_level)
    );

    assign led_red = veto_out;
    assign led_green = ~veto_out & sensor_valid;
endmodule