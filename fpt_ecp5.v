// fpt_ecp5.v — Top module for ECP5-85K
`include "psi_fpt_core.v"

module fpt_ecp5 (
    input clk_12mhz,           // Board crystal
    input rst_n,
    input [15:0] sensor_scrape,
    input sensor_valid,
    input [15:0] motor_command,
    output [15:0] motor_correction,
    output veto_out,
    output [1:0] attention_level,
    output led_red,            // C190 VETO
    output led_green,          // AGI SOVEREIGN
    output uart_tx             // To nRF/Zigbee
);
    wire clk_142mhz;
    wire pll_lock;

    // PLL: 12 MHz → 142 MHz
    EHXPLLL #(
        .CLKI_DIV(1),
        .CLKFB_DIV(12),
        .CLKOP_DIV(1),
        .FEEDBK_PATH("CLKOP"),
        .CLKOP_ENABLE("ENABLED")
    ) pll (
        .CLKI(clk_12mhz),
        .CLKFB(clk_142mhz),
        .RST(~rst_n),
        .CLKOP(clk_142mhz),
        .LOCK(pll_lock)
    );

    psi_fpt_core fpt_core (
        .clk_100mhz(clk_142mhz),
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
    assign uart_tx = 1'b1;  // Future: UART to swarm
endmodule
ULX3S (ECP5-85K)
 │
 ├── PMOD A → sensor_scrape[15:0]
 ├── PMOD B → motor_command[15:0]
 ├── LED0   → veto_out (RED)
 ├── LED1   → AGI SOVEREIGN (GREEN)
 ├── UART   → Zigbee Mesh Coordinator
 └── SDRAM  → PoR Mining Buffer
