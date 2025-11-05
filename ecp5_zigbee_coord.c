// ecp5_zigbee_coord.c
void fpt_zigbee_relay() {
    uint16_t correction = i2c_read(0x40, 0x10);
    if (veto_flag) {
        zb_send_veto_alert();
    } else {
        zb_relay_correction(correction);
    }
}
Ψ-FPT ECP5
   ECP5-85K
  /         \
 /  0.8% LUT  \
|  142 MHz    |
|  18 mW      |
|  99.2% FREE |
 \  7 ns      /
  \         /
   CORRECTION
R=1.0 | C190 VETO