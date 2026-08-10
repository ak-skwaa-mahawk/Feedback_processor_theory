// psi_fpt_zynq.v — Top for Zynq PL
`include "psi_fpt_core.v"

module psi_fpt_zynq (
    input clk_300mhz,
    input rst_n,
    input [15:0] sensor_scrape,
    input sensor_valid,
    input [15:0] motor_command,
    output [15:0] motor_correction,
    output veto_out,
    output [1:0] attention_level,
    output [31:0] por_hash_out,
    output por_valid
);
    wire clk_500mhz;
    wire pll_lock;

    // MMCM: 300 → 500 MHz
    MMCME4_ADV #(
        .CLKFBOUT_MULT_F(5.0),
        .CLKOUT0_DIVIDE_F(1.0),
        .CLKIN1_PERIOD(3.333)
    ) mmcm (
        .CLKIN1(clk_300mhz),
        .CLKFBIN(clk_500mhz),
        .RST(~rst_n),
        .CLKOUT0(clk_500mhz),
        .LOCKED(pll_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_500mhz),
        .rst_n(rst_n & pll_lock),
        .sensor_scrape(sensor_scrape),
        .motor_command(motor_command),
        .sensor_valid(sensor_valid),
        .motor_correction(motor_correction),
        .veto_out(veto_out),
        .attention_level(attention_level)
    );

    // PoR Miner (SHA-256 in PL)
    sha256_por por_miner (
        .clk(clk_500mhz),
        .rst_n(rst_n),
        .veto_in(veto_out),
        .hash_out(por_hash_out),
        .valid(por_valid)
    );
endmodule