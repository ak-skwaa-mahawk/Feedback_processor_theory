// reafference_comparator.v
// Greenwald: Compare actual vs expected (imaged reafference)
module reafference_comparator #(
    parameter WIDTH = 16
)(
    input clk,
    input rst_n,
    input [WIDTH-1:0] scrape,        // Sensor input
    input [WIDTH-1:0] ref_glyph,     // Expected (from motor efference copy)
    output reg [WIDTH-1:0] error_raw,
    output reg error_valid
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            error_raw <= 0;
            error_valid <= 0;
        end else begin
            error_raw <= scrape - ref_glyph;  // Signed error
            error_valid <= 1;
        end
    end
endmodule