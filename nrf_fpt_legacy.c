// nrf_fpt_legacy.c (nRF51822)
void fpt_spartan_bridge() {
    uint16_t correction;
    if (i2c_read(0x40, 0x10, &correction)) {
        if (veto_flag) {
            LOG_WRN("C190 VETO FROM SPARTAN-6");
        } else {
            motor_set(correction);
        }
    }
}
Ψ-FPT SPARTAN-6
   XC6SLX16
  /         \
 /  5.4% LUT  \
|  100 MHz    |
|  50 mW      |
|  10 ns      |
|  2+ YR BAT  |
 \  1 CYCLE   /
  \         /
   LEGACY CORE
R=1.0 | C190 VETO