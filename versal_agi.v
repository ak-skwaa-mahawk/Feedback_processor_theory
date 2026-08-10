// versal_agi.v — AGI Healer (Synthesizable & Latch-Free)
module versal_agi (
    input clk_650mhz,
    input rst_n,               // Asynchronous active-low master reset
    input sefi_flag,           // Critical single event interruption signal
    output reg veto,
    output reg dpr_start,
    output reg ai_redundancy_shift
);
    // Synchronous state capture at 650 MHz (1.53ns period)
    always @(posedge clk_650mhz or negedge rst_n) begin
        if (!rst_n) begin
            veto                <= 1'b0;
            dpr_start           <= 1'b0;
            ai_redundancy_shift <= 1'b0;
        end else begin
            if (sefi_flag) begin
                veto                <= 1'b1;
                dpr_start           <= 1'b1;
                ai_redundancy_shift <= 1'b1; // Fault isolation fallback
            end else begin
                veto                <= 1'b0; // Explicitly clear all registers
                dpr_start           <= 1'b0; // Prevents compiler latch inference
                ai_redundancy_shift <= 1'b0;
            end
        end
    end
endmodule
