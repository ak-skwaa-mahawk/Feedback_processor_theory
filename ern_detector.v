// ern_detector.v
// ERN/FRN: Mid-frontal theta burst on error
module ern_detector #(
    parameter THRESH = 100  // |error| > THRESH → ERN
)(
    input clk,
    input rst_n,
    input signed [15:0] error_raw,
    input error_valid,
    output reg ern_pulse,
    output reg [7:0] theta_power  // Mock theta (4–8 Hz)
);
    reg [15:0] error_abs;
    reg [3:0] theta_counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ern_pulse <= 0;
            theta_counter <= 0;
        end else if (error_valid) begin
            error_abs = (error_raw[15]) ? -error_raw : error_raw;
            ern_pulse <= (error_abs > THRESH);
            theta_counter <= theta_counter + 1;
            if (theta_counter == 15) theta_counter <= 0;
            theta_power <= ern_pulse ? 8'd200 : 8'd50;
        end
    end
endmodule