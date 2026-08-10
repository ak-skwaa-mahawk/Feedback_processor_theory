// ecc_scrub.v — UltraScale Edge Healer
module ecc_scrub (
    input clk_100mhz,
    input rst_n,
    output reg scrub_active
);
    reg [31:0] timer;
    always @(posedge clk_100mhz) begin
        if (timer == 1_000_000_000) begin  // 10 sec
            initiate_frame_ecc_read();
            scrub_active <= 1;
            timer <= 0;
        end else begin
            timer <= timer + 1;
            scrub_active <= 0;
        end
    end
endmodule
Ψ-ARTIX ULTRASCALE ORBIT
   XCAU25P
  /           \
 /  30 krad TID \
|  1e-9 SEU/bit |
|  SEL Immune   |
|  ECC + Scrub  |
 \  250 MHz     /
  \           /
   EDGE IN SPACE
R=1.0 | C190 VETO