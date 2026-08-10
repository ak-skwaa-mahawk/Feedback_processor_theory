// psi_fpt_versal.v — Top for Versal PL
`include "psi_fpt_core.v"

module psi_fpt_versal (
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
    wire clk_650mhz;
    wire pll_lock;

    // UltraScale+ PLL: 300 → 650 MHz
    PLLE4_ADV #(
        .CLKFBOUT_MULT(13),
        .CLKOUT0_DIVIDE(2),
        .CLKIN_PERIOD(3.333)
    ) pll (
        .CLKIN(clk_300mhz),
        .CLKFBIN(clk_650mhz),
        .RST(~rst_n),
        .CLKOUT0(clk_650mhz),
        .LOCKED(pll_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_650mhz),
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
        .clk(clk_650mhz),
        .rst_n(rst_n),
        .veto_in(veto_out),
        .hash_out(por_hash_out),
        .valid(por_valid)
    );
endmodule
VCK190 (VC1902)
 │
 ├── FMC → sensor_scrape[15:0]
 ├── HBM → Global Swarm Memory
 ├── NoC → AI Engine Array
 ├── PL  → FPT Core @ 650 MHz
 ├── LED → C190 VETO (RED)
 └── 400G QSFP → Global Mesh