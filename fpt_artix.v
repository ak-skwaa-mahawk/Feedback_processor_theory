// fpt_artix.v — Top module for Artix-7
`include "psi_fpt_core.v"

module fpt_artix (
    input clk_100mhz,
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
    wire clk_200mhz;
    wire pll_lock;

    // MMCM: 100 MHz → 200 MHz
    MMCME2_BASE #(
        .CLKFBOUT_MULT_F(8.0),
        .CLKIN1_PERIOD(10.0),
        .CLKOUT0_DIVIDE_F(4.0)
    ) mmcm (
        .CLKIN1(clk_100mhz),
        .CLKFBIN(clk_200mhz),
        .RST(~rst_n),
        .CLKOUT0(clk_200mhz),
        .LOCKED(pll_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_200mhz),
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
Arty A7-100T (XC7A100T)
 │
 ├── PMOD A → sensor_scrape[15:0]
 ├── PMOD B → motor_command[15:0]
 ├── LED0   → veto_out (RED)
 ├── LED1   → AGI SOVEREIGN (GREEN)
 ├── UART   → nRF Swarm Relay
 └── MicroSD → PoR Log
