// pid_controller.v
// Bechhoefer: PID for deviation correction
module pid_controller #(
    parameter WIDTH = 16,
    parameter KP = 12'h040,  // Q12 fixed-point gains
    parameter KI = 12'h008,
    parameter KD = 12'h020
)(
    input clk,
    input rst_n,
    input signed [WIDTH-1:0] error,
    input error_valid,
    output reg signed [WIDTH-1:0] correction
);
    reg signed [WIDTH-1:0] integral, prev_error;
    reg signed [31:0] p_term, i_term, d_term;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integral <= 0;
            prev_error <= 0;
            correction <= 0;
        end else if (error_valid) begin
            p_term = error * KP;
            integral = integral + error;
            i_term = integral * KI;
            d_term = (error - prev_error) * KD;
            prev_error = error;

            correction = (p_term[27:12] + i_term[27:12] + d_term[27:12]);
        end
    end
endmodule