// pid_fpt.v — Hardware FPT
module pid_fpt (
    input clk,
    input [15:0] actual, expected,
    output reg [7:0] veto
);
    wire [15:0] error = expected - actual;
    always @(posedge clk) begin
        if (error > THRESHOLD) veto <= 1;
        else veto <= 0;
    end
endmodule