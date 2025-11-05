// zynq_seu_healer.v — Hybrid Sovereign
module zynq_seu_healer (
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
            initiate_partial_reconfig();
        end else begin
            veto_pulse <= 0;
        end
    end
endmodule
