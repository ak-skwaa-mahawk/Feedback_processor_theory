// tmr_with_dpr.v — SEU Adaptive
module tmr_dpr (
    input clk,
    input [1:0] votes,  // From 3 modules
    output reg out,
    output reg reconfig_flag
);
    always @(*) begin
        case (votes)
            2'b00: out = 0;  // Majority 0
            2'b01: out = 0;
            2'b10: out = 1;
            2'b11: out = 1;
            default: begin out = 0; reconfig_flag = 1; end
        endcase
    end
endmodule