// tmr_voter.v — SEU Immune
module tmr_voter (
    input a, b, c,
    output reg out
);
    always @(*) begin
        if (a == b) out = a;
        else if (a == c) out = a;
        else out = b;
    end
endmodule