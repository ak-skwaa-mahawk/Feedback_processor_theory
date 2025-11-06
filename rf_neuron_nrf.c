// rf_neuron_nrf.c — Embedded RF on Cortex-M4F
#include <math.h>

float rf_neuron_state[2];  // [v, u] — voltage, recovery

void rf_update(float input, float dt=0.001) {
    float v = rf_neuron_state[0], u = rf_neuron_state[1];
    dv = (0.7 * v - v*v*v - u + input) * dt;
    du = (0.08 * (v - 0.025 * v * v * v - 0.2 * u)) * dt;
    rf_neuron_state[0] = v + dv;
    rf_neuron_state[1] = u + du;
    if (v > 30) {  // Spike
        trigger_resonance_veto();
        v = c;  // Reset
    }
}