`timescale 1ns / 1ps

module test_power_fsm;
    reg clk, rst_n;
    reg [15:0] harvest_level;
    reg [7:0] threat_level;
    reg [15:0] energy_reserve;
    reg emergency_override;
    
    wire [7:0] acoustic_duty_cycle;
    wire [7:0] spectral_duty_cycle;
    wire [7:0] mesh_duty_cycle;
    wire [1:0] power_state;
    wire recalibration_request;
    
    power_fsm dut (
        .clk(clk),
        .rst_n(rst_n),
        .harvest_level(harvest_level),
        .threat_level(threat_level),
        .energy_reserve(energy_reserve),
        .emergency_override(emergency_override),
        .acoustic_duty_cycle(acoustic_duty_cycle),
        .spectral_duty_cycle(spectral_duty_cycle),
        .mesh_duty_cycle(mesh_duty_cycle),
        .power_state(power_state),
        .recalibration_request(recalibration_request)
    );
    
    // Clock generation (10MHz)
    initial clk = 0;
    always #50 clk = ~clk;
    
    // Test sequence
    initial begin
        $dumpfile("power_fsm.vcd");
        $dumpvars(0, test_power_fsm);
        
        // Initialize
        rst_n = 0;
        harvest_level = 16'h4000;  // Medium harvest
        threat_level = 8'h00;      // No threat
        energy_reserve = 16'h8000; // High reserves
        emergency_override = 0;
        
        #100 rst_n = 1;
        
        // Test 1: Normal surveillance
        #1000;
        assert(power_state == 2'b01) else $error("Should be in SURVEILLANCE");
        assert(acoustic_duty_cycle == 8'd26) else $error("Wrong acoustic duty");
        
        // Test 2: Threat detected → ALERT
        threat_level = 8'h30;
        #1000;
        assert(power_state == 2'b10) else $error("Should transition to ALERT");
        assert(acoustic_duty_cycle == 8'd128) else $error("Should increase duty");
        
        // Test 3: High threat + energy → ATTACK
        threat_level = 8'h90;
        energy_reserve = 16'hA000;
        #1000;
        assert(power_state == 2'b11) else $error("Should transition to ATTACK");
        assert(acoustic_duty_cycle == 8'd255) else $error("Should be max power");
        
        // Test 4: Energy depletion → back to SURVEILLANCE
        energy_reserve = 16'h0800;
        #1000;
        assert(power_state == 2'b01) else $error("Should drop to SURVEILLANCE");
        
        // Test 5: Low energy + no threat → HIBERNATE
        threat_level = 8'h00;
        energy_reserve = 16'h0400;
        harvest_level = 16'h0800;
        #1000;
        assert(power_state == 2'b00) else $error("Should enter HIBERNATE");
        assert(acoustic_duty_cycle == 8'd3) else $error("Should be minimal power");
        
        // Test 6: Emergency override
        emergency_override = 1;
        #100;
        assert(power_state == 2'b11) else $error("Override should force ATTACK");
        emergency_override = 0;
        
        $display("All tests passed!");
        $finish;
    end
    
    // Timeout
    initial #100000 $finish;
endmodule