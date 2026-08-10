// fpt_spartan.v — Top module for Spartan-6
`include "psi_fpt_core.v"

module fpt_spartan (
    input clk_50mhz,
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
    wire clk_100mhz;
    wire dcm_lock;

    // DCM: 50 MHz → 100 MHz
    DCM_SP #(
        .CLKFX_MULTIPLY(2),
        .CLKFX_DIVIDE(1),
        .CLKIN_PERIOD(20.0)
    ) dcm (
        .CLKIN(clk_50mhz),
        .CLKFB(clk_100mhz),
        .RST(~rst_n),
        .CLKFX(clk_100mhz),
        .LOCKED(dcm_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_100mhz),
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
SP605 (XC6SLX16)
 │
 ├── FMC → sensor_scrape[15:0]
 ├── LED0   → veto_out (RED)
 ├── LED1   → AGI SOVEREIGN (GREEN)
 ├── UART   → nRF Legacy Relay
 └── CompactFlash → PoR Log