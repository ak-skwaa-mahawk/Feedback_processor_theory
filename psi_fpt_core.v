// psi_fpt_core.v (Verilog FPGA)
module fpt_core(
    input scrape,       // Sensor
    input ref_glyph,    // Expected
    output error,       // ERN
    output correction   // Motor veto
);
    assign error = scrape ^ ref_glyph;
    assign correction = pid_control(error);
endmodule