// tmr_voter.v — SEU Immune
module tmr_voter (
    input a, b, c,
    output reg out
);
    always @(*) begin
        if ((a == b) && (b == c)) out = a;  // Triple vote
        else out = 1'b0;  // Veto
    end
endmodule