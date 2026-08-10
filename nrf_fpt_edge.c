// nrf_fpt_edge.c (Zephyr)
void fpt_artix_bridge() {
    uint16_t correction;
    i2c_reg_read_byte_dt(&i2c_dev, 0x40, 0x10, (uint8_t*)&correction);
    if (veto_flag) {
        LOG_WRN("C190 VETO FROM ARTIX-7");
    } else {
        motor_set(correction);
    }
}
Ψ-FPT ARTIX-7
   XC7A100T
  /         \
 /  1.1% LUT  \
|  200 MHz    |
|  80 mW      |
|  5 ns       |
 \  1 CYCLE   /
  \         /
   EDGE CORE
R=1.0 | C190 VETO