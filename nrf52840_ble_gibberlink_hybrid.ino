// nrf52840_ble_gibberlink_hybrid.ino
if (provisioner_dies || rf_jamming_detected) {
    ble_mesh_disable();
    gibberlink_resonance_activate();   // switch to ultrasonic + Li-Fi + photon
    glyph_teleport_via_quantum_repeater();
}