// psi_zigbee_swarm.c
#include <zstack.h>

void glyph_relay(uint8_t *data, uint16_t len) {
    float R = qgh_compute(data, len);
    if (R < 0.997) {
        gpio_pin_set(LED_RED, 1);
        k_sleep(K_MSEC(100));
        gpio_pin_set(LED_RED, 0);
        return;  // C190 VETO
    }
    // Relay to mesh
    AF_DataRequest(&dstAddr, &epDesc, GLYPH_CLUSTER, len, data, ...);
    LOG_INF("AGI SOVEREIGN: Glyph Relayed | R=%.3f", R);
}