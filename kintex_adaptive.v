// kintex_adaptive.v — Adaptive Healer
module kintex_adaptive (
    input clk_500mhz,
    input rst_n,
    input sefi_flag,
    output reg dpr_start,
    output reg veto_pulse
);
    always @(posedge clk_500mhz) begin
        if (sefi_flag) begin
            veto_pulse <= 1;
            dpr_start <= 1;
            initiate_dpr_fpt();
        end else begin
            veto_pulse <= 0;
        end
    end
endmodule
Ψ-KINTEX ULTRASCALE ADAPTIVE
   XCKU115 / XQRKU115
  /                 \
 /  150–300 krad TID  \
|  <6e-10 SEU/bit      |
|  SEL Immune          |
|  ECC + DPR 25 ms     |
|  1.1M LUTs + 28G     |
 \  500 MHz           /
  \                 /
   ADAPTIVE CORE
R=1.0 | C190 VETO