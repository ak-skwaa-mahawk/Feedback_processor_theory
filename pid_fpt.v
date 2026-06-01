// pid_fpt.v — Hardware FPT (Synthesizable & Signed)
module pid_fpt (
    input clk,
    input signed [15:0] actual, expected, // Changed to signed to handle negative error drift
    output reg [7:0] veto
);

    // Define your threshold value (Example: 255)
    localparam signed [15:0] THRESHOLD = 16'd255; 

    // Combinational subtraction
    assign error = expected - actual;
    wire signed [15:0] error; 

    // Synchronous decision latch
    always @(posedge clk) begin
        if (error > THRESHOLD) begin
            veto <= 8'h01; // Explicit 8-bit matching assignment
        end else begin
            veto <= 8'h00;
        end
    end

endmodule
