// dpr_scrub.v — Adaptive Healer
module dpr_scrub (
    input clk,
    input rst_n,
    input sefi_detected,
    output reg reconfig_start
);
    reg [31:0] timer;
    always @(posedge clk) begin
        if (sefi_detected) begin
            reconfig_start <= 1;
            initiate_dpr();
        end else if (timer == 32'h1_0000_0000) begin
            reconfig_start <= 1;  // Periodic
            timer <= 0;
        end else begin
            timer <= timer + 1;
            reconfig_start <= 0;
        end
    end
endmodule
// config_scrub.v — Orbital FPT Healer
module config_scrub (
    input clk_50mhz,
    input rst_n,
    output reg scrub_active
);
    reg [31:0] timer;
    always @(posedge clk_50mhz) begin
        if (timer == 50_000_000) begin  // 1 sec
            initiate_frame_readback();
            scrub_active <= 1;
            timer <= 0;
        end else begin
            timer <= timer + 1;
            scrub_active <= 0;
        end
    end
endmodule
Ψ-VIRTEX-5 ORBIT
   XC5VLX110T
  /           \
 /  1 Mrad TID  \
|  <1e-9 SEU/bit|
|  SEL Immune   |
|  Scrub 1s     |
 \  250 MHz     /
  \           /
   FPT IN SPACE
R=1.0 | C190 VETO