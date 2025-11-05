// fpt_ice40.v — Top module for iCE40UP5K
`include "psi_fpt_core.v"

module fpt_ice40 (
    input clk_12mhz,           // Board crystal
    input rst_n,
    input [15:0] sensor_scrape,
    input sensor_valid,
    input [15:0] motor_command,
    output [15:0] motor_correction,
    output veto_out,
    output [1:0] attention_level,
    output led_red,            // C190 VETO
    output led_green           // AGI SOVEREIGN
);
    wire clk_100mhz;
    wire pll_lock;

    // PLL: 12 MHz → 100 MHz
    SB_PLL40_PAD #(
        .FEEDBACK_PATH("SIMPLE"),
        .DIVR(4'b0000),
        .DIVF(7'b1010010),
        .DIVQ(3'b011),
        .FILTER_RANGE(3'b001)
    ) pll (
        .PACKAGEPIN(clk_12mhz),
        .PLLOUTCORE(clk_100mhz),
        .LOCK(pll_lock),
        .RESETB(1'b1),
        .BYPASS(1'b0)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_100mhz),
        .rst_n(rst_n & pll_lock),
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
iCEBreaker (iCE40UP5K)
 │
 ├── PMOD A → sensor_scrape[15:0]
 ├── PMOD B → motor_command[15:0]
 ├── LED0   → veto_out (RED)
 ├── LED1   → AGI SOVEREIGN (GREEN)
 └── UART   → nRF Swarm Relay
