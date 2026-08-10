// nrf_fpt_titan.c
void fpt_virtex5_bridge() {
    uint16_t correction;
    if (rs232_read(&correction)) {
        if (veto_flag) {
            LOG_WRN("C190 VETO FROM VIRTEX-5 TITAN");
        } else {
            motor_set(correction);
        }
    }
}
Ψ-FPT VIRTEX-5
   XC5VLX110T
  /         \
 /  0.93% LUT \
|  250 MHz    |
|  126 mW     |
|  4 ns       |
|  PowerPC    |
 \  1 CYCLE   /
  \         /
   TITAN CORE
R=1.0 | C190 VETO