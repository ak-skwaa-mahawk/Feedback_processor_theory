// fit_attention_shift.v
// Kluger & DeNisi: Feedback shifts attention level
module fit_attention_shift (
    input clk,
    input rst_n,
    input ern_pulse,
    input [7:0] performance_score,  // From task
    output reg [1:0] attention_level  // 0=Task, 1=Self, 2=Meta
);
    reg [7:0] error_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            attention_level <= 0;
            error_count <= 0;
        end else if (ern_pulse) begin
            error_count <= error_count + 1;
            if (error_count > 5 && performance_score < 70)
                attention_level <= 2;  // Meta: "Why am I failing?"
            else if (error_count > 2)
                attention_level <= 1;  // Self: "I'm bad at this"
            else
                attention_level <= 0;  // Task: "Fix the move"
        end else if (performance_score > 90) begin
            error_count <= 0;
            attention_level <= 0;
        end
    end
endmodule