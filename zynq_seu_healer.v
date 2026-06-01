cat > zynq_seu_healer.v << 'EOF'
// zynq_seu_healer.v — Hybrid Sovereign (Synthesizable State Machine)
module zynq_seu_healer (
    input clk_500mhz,
    input rst_n,
    input sefi_flag,       // High if a Single Event Functional Interruption occurs
    input dpr_done,        // Input from PCAP/ICAP indicating reconfiguration finished
    output reg dpr_start,  // Triggers the configuration engine
    output reg veto_pulse  // Isolates downstream logic during recovery
);

    // State Encoding using localparams
    localparam STATE_IDLE     = 2'b00;
    localparam STATE_SCRUB    = 2'b01;
    localparam STATE_RECOVER  = 2'b10;

    reg [1:0] current_state, next_state;

    // 1. Sequential State Transition Layer (2ns Timing Target)
    always @(posedge clk_500mhz or negedge rst_n) begin
        if (!rst_n) 
            current_state <= STATE_IDLE;
        else 
            current_state <= next_state;
    end

    // 2. Combinatorial Next-State Logic Gating
    always @(*) begin
        next_state = current_state;
        case (current_state)
            STATE_IDLE: begin
                if (sefi_flag) next_state = STATE_SCRUB;
            end
            STATE_SCRUB: begin
                // Remain in scrub state until hardware indicates completion
                if (dpr_done) next_state = STATE_RECOVER;
            end
            STATE_RECOVER: begin
                // 1-cycle cooldown state to let pipelines settle
                next_state = STATE_IDLE;
            end
            default: next_state = STATE_IDLE;
        endcase
    end

    // 3. Registered Outputs Layer (Eliminates Glitches / Preserves Setup Time)
    always @(posedge clk_500mhz or negedge rst_n) begin
        if (!rst_n) begin
            veto_pulse <= 1'b0;
            dpr_start  <= 1'b0;
        end else begin
            case (next_state)
                STATE_IDLE: begin
                    veto_pulse <= 1'b0;
                    dpr_start  <= 1'b0;
                end
                STATE_SCRUB: begin
                    veto_pulse <= 1'b1; // Hold veto line high to shield logic
                    dpr_start  <= 1'b1; // Pulse or hold the start bit
                end
                STATE_RECOVER: begin
                    veto_pulse <= 1'b1; // Keep veto high while clocks stabilize
                    dpr_start  <= 1'b0;
                end
            endcase
        end
    end

endmodule
EOF
