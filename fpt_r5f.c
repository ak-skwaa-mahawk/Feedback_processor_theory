// fpt_r5f.c — Real-Time FPT on Cortex-R5F
#include "xil_printf.h"
#include "fpt_qgh.h"

void fpt_realtime_task() {
    uint16_t scrape, ref;
    float R;

    while (1) {
        if (xil_i2c_read(&scrape) && xil_i2c_read(&ref)) {
            R = qgh_256_compute(scrape, ref);
            if (R < 0.997f) {
                xil_gpio_set(VETO_PIN);
                xil_printf("C190 VETO | R=%.3f\n", R);
            } else {
                xil_gpio_clr(VETO_PIN);
            }
        }
        // 1.6 µs loop
    }
}