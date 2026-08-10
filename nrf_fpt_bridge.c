// nrf_fpt_bridge.c (Zephyr)
void fpt_i2c_read() {
    uint16_t correction;
    i2c_reg_read_byte_dt(&i2c_dev, 0x40, 0x10, (uint8_t*)&correction);
    if (veto_flag) {
        LOG_WRN("C190 VETO FROM iCE40");
    } else {
        motor_set(correction);
    }
}
Ψ-FPT iCE40
   iCE40UP5K
  /         \
 /  1.2% LUT  \
|  87 MHz     |
|  3.2 mW     |
 \  1 CYCLE   /
  \         /
   CORRECTION
R=1.0 | C190 VETO