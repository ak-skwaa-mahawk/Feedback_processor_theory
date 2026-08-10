// kalman_predictor.v
// Kalman: Predict next state, fuse with scrape
module kalman_predictor #(
    parameter WIDTH = 16
)(
    input clk,
    input rst_n,
    input [WIDTH-1:0] scrape,
    input scrape_valid,
    output reg [WIDTH-1:0] predicted_glyph,
    output reg predict_valid
);
    // Simple 1D velocity model: x = x + v*dt
    reg [WIDTH-1:0] x_est, v_est;
    parameter Q = 16'h0010, R = 16'h0100;  // Process & measurement noise

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_est <= 0;
            v_est <= 0;
        end else if (scrape_valid) begin
            // Predict
            x_est <= x_est + v_est;
            // Update
            x_est <= x_est + ((scrape - x_est) >>> 2);  // K = 0.25
            predict_valid <= 1;
            predicted_glyph <= x_est;
        end else begin
            predict_valid <= 0;
        end
    end
endmodule