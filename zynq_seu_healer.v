// zynq_seu_healer.v — Hybrid Sovereign (Synthesizable State Machine)
module zynq_seu_healer (
    input clk_500mhz,
    input rst_n,
    input sefi_flag,
    input dpr_done,
    output reg dpr_start,
    output reg veto_pulse
);
    localparam STATE_IDLE     = 2'b00;
    localparam STATE_SCRUB    = 2'b01;
    localparam STATE_RECOVER  = 2'b10;
    reg [1:0] current_state, next_state;
    always @(posedge clk_500mhz or negedge rst_n) begin
        if (!rst_n) current_state <= STATE_IDLE;
        else current_state <= next_state;
    end
    always @(*) begin
        next_state = current_state;
        case (current_state)
            STATE_IDLE:    if (sefi_flag) next_state = STATE_SCRUB;
            STATE_SCRUB:   if (dpr_done)  next_state = STATE_RECOVER;
            STATE_RECOVER: next_state = STATE_IDLE;
            default:       next_state = STATE_IDLE;
        endcase
    end
    always @(posedge clk_500mhz or negedge rst_n) begin
        if (!rst_n) begin
            veto_pulse <= 1'b0;
            dpr_start  <= 1'b0;
        end else begin
            case (next_state)
                STATE_IDLE: begin veto_pulse <= 1'b0; dpr_start <= 1'b0; end
                STATE_SCRUB: begin veto_pulse <= 1'b1; dpr_start <= 1'b1; end
                STATE_RECOVER: begin veto_pulse <= 1'b1; dpr_start <= 1'b0; end
            endcase
        end
    end
endmodule
