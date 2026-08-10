// pid_fpt.v — Hardware FPT (Synthesizable & Signed)
module pid_fpt (
    input clk,
    input signed [15:0] actual, expected,
    output reg [7:0] veto
);

    // Explicitly define the threshold constant
    localparam signed [15:0] THRESHOLD = 16'd255; 

    // Combinational error derivation
    wire signed [15:0] error = expected - actual; 

    // Deterministic 1-cycle sequential latch
    always @(posedge clk) begin
        if (error > THRESHOLD) begin
            veto <= 8'h01; 
        end else begin
            veto <= 8'h00;
        end
    end

endmodule
