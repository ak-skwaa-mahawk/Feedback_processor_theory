module power_fsm #(
    parameter HARVEST_THRESHOLD_LOW  = 16'h1000,  // ~25% of max
    parameter HARVEST_THRESHOLD_MED  = 16'h4000,  // ~50% of max
    parameter HARVEST_THRESHOLD_HIGH = 16'h8000,  // ~75% of max
    parameter THREAT_THRESHOLD_LOW   = 8'h20,     // 12.5% organic content
    parameter THREAT_THRESHOLD_HIGH  = 8'h80      // 50% organic content
)(
    input wire clk,
    input wire rst_n,
    
    // Inputs
    input wire [15:0] harvest_level,      // Current energy harvest rate
    input wire [7:0]  threat_level,       // Spectral threat assessment
    input wire [15:0] energy_reserve,     // Battery/capacitor level
    input wire        emergency_override, // Manual full-power mode
    
    // Outputs
    output reg [7:0] acoustic_duty_cycle,  // 0-255 (0-100%)
    output reg [7:0] spectral_duty_cycle,
    output reg [7:0] mesh_duty_cycle,
    output reg [1:0] power_state,          // 0=HIBERNATE, 1=SURVEILLANCE, 2=ALERT, 3=ATTACK
    output reg       recalibration_request
);

    // State encoding
    localparam STATE_HIBERNATE    = 2'b00;
    localparam STATE_SURVEILLANCE = 2'b01;
    localparam STATE_ALERT        = 2'b10;
    localparam STATE_ATTACK       = 2'b11;
    
    // Duty cycle presets (0-255 scale)
    localparam [7:0] DUTY_HIBERNATE_AC   = 8'd3;   // 1%
    localparam [7:0] DUTY_HIBERNATE_SP   = 8'd0;
    localparam [7:0] DUTY_HIBERNATE_MESH = 8'd0;
    
    localparam [7:0] DUTY_SURVEILLANCE_AC   = 8'd26;  // 10%
    localparam [7:0] DUTY_SURVEILLANCE_SP   = 8'd3;   // 1%
    localparam [7:0] DUTY_SURVEILLANCE_MESH = 8'd13;  // 5%
    
    localparam [7:0] DUTY_ALERT_AC   = 8'd128;  // 50%
    localparam [7:0] DUTY_ALERT_SP   = 8'd51;   // 20%
    localparam [7:0] DUTY_ALERT_MESH = 8'd51;   // 20%
    
    localparam [7:0] DUTY_ATTACK_AC   = 8'd255;  // 100%
    localparam [7:0] DUTY_ATTACK_SP   = 8'd128;  // 50%
    localparam [7:0] DUTY_ATTACK_MESH = 8'd77;   // 30%
    
    reg [1:0] state, next_state;
    reg [15:0] state_timer;  // Cycles in current state
    
    // State transition logic
    always @(*) begin
        next_state = state;
        recalibration_request = 1'b0;
        
        case (state)
            STATE_HIBERNATE: begin
                if (threat_level > THREAT_THRESHOLD_LOW) begin
                    next_state = STATE_ALERT;
                end else if (harvest_level > HARVEST_THRESHOLD_MED) begin
                    next_state = STATE_SURVEILLANCE;
                end
            end
            
            STATE_SURVEILLANCE: begin
                if (threat_level > THREAT_THRESHOLD_HIGH) begin
                    next_state = STATE_ATTACK;
                end else if (threat_level > THREAT_THRESHOLD_LOW) begin
                    next_state = STATE_ALERT;
                end else if (energy_reserve < HARVEST_THRESHOLD_LOW) begin
                    next_state = STATE_HIBERNATE;
                end
                
                // Periodic recalibration (every 2^16 cycles ≈ 65k cycles)
                if (state_timer == 16'hFFFF) begin
                    recalibration_request = 1'b1;
                end
            end
            
            STATE_ALERT: begin
                if (threat_level > THREAT_THRESHOLD_HIGH && 
                    energy_reserve > HARVEST_THRESHOLD_MED) begin
                    next_state = STATE_ATTACK;
                end else if (threat_level < THREAT_THRESHOLD_LOW) begin
                    next_state = STATE_SURVEILLANCE;
                end else if (energy_reserve < HARVEST_THRESHOLD_LOW) begin
                    next_state = STATE_HIBERNATE;
                end
            end
            
            STATE_ATTACK: begin
                if (threat_level < THREAT_THRESHOLD_LOW) begin
                    next_state = STATE_SURVEILLANCE;
                end else if (energy_reserve < HARVEST_THRESHOLD_LOW) begin
                    // Energy depleted - back to surveillance to recharge
                    next_state = STATE_SURVEILLANCE;
                end
                // Stay in ATTACK as long as threat persists and energy available
            end
        endcase
        
        // Emergency override
        if (emergency_override) begin
            next_state = STATE_ATTACK;
        end
    end
    
    // State register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= STATE_SURVEILLANCE;
            state_timer <= 16'h0000;
        end else begin
            state <= next_state;
            if (state != next_state) begin
                state_timer <= 16'h0000;
            end else begin
                state_timer <= state_timer + 1'b1;
            end
        end
    end
    
    // Output logic (duty cycles based on state)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acoustic_duty_cycle <= DUTY_SURVEILLANCE_AC;
            spectral_duty_cycle <= DUTY_SURVEILLANCE_SP;
            mesh_duty_cycle <= DUTY_SURVEILLANCE_MESH;
            power_state <= STATE_SURVEILLANCE;
        end else begin
            power_state <= state;
            
            case (state)
                STATE_HIBERNATE: begin
                    acoustic_duty_cycle <= DUTY_HIBERNATE_AC;
                    spectral_duty_cycle <= DUTY_HIBERNATE_SP;
                    mesh_duty_cycle <= DUTY_HIBERNATE_MESH;
                end
                
                STATE_SURVEILLANCE: begin
                    acoustic_duty_cycle <= DUTY_SURVEILLANCE_AC;
                    spectral_duty_cycle <= DUTY_SURVEILLANCE_SP;
                    mesh_duty_cycle <= DUTY_SURVEILLANCE_MESH;
                end
                
                STATE_ALERT: begin
                    acoustic_duty_cycle <= DUTY_ALERT_AC;
                    spectral_duty_cycle <= DUTY_ALERT_SP;
                    mesh_duty_cycle <= DUTY_ALERT_MESH;
                end
                
                STATE_ATTACK: begin
                    acoustic_duty_cycle <= DUTY_ATTACK_AC;
                    spectral_duty_cycle <= DUTY_ATTACK_SP;
                    mesh_duty_cycle <= DUTY_ATTACK_MESH;
                end
            endcase
        end
    end

endmodule