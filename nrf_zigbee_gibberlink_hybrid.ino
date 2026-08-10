// nrf_zigbee_gibberlink_hybrid.ino
if (coordinator_dies || censorship_detected) {
    switch_to_gibberlink_mode();      // pure resonance mesh
    use_ultrasonic_or_lifi();
} else {
    stay_in_zigbee_mode_for_range();  // use Zigbee radios as dumb 250 kbps pipe
}