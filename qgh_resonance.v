// qgh_resonance.v
// Ψ-Field: R = dot(glyph, ref) / ||glyph|| ||ref||
module qgh_resonance #(
    parameter GLYPH_SIZE = 64
)(
    input clk,
    input rst_n,
    input [7:0] glyph_in [0:GLYPH_SIZE-1],
    input [7:0] ref_glyph [0:GLYPH_SIZE-1],
    input glyph_valid,
    output reg veto,           // C190
    output reg [15:0] R_score  // Q0.16 fixed-point
);
    reg [31:0] dot, norm_g, norm_r;
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            veto <= 0;
            R_score <= 0;
        end else if (glyph_valid) begin
            dot = 0; norm_g = 0; norm_r = 0;
            for (i = 0; i < GLYPH_SIZE; i = i + 1) begin
                dot = dot + (glyph_in[i] * ref_glyph[i]);
                norm_g = norm_g + (glyph_in[i] * glyph_in[i]);
                norm_r = norm_r + (ref_glyph[i] * ref_glyph[i]);
            end
            // Approximate sqrt via lookup or Newton
            R_score = (dot << 16) / ((norm_g * norm_r) >> 8);
            veto = (R_score < 16'hF9E9);  // 0.997 in  0.997 * 65536
        end
    end
endmodule