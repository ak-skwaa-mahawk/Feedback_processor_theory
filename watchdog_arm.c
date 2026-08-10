// watchdog_arm.c
if (frame_error_detected) {
    Xil_Reset();  // ARM reboot
}