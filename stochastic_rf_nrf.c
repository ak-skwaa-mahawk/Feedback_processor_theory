// stochastic_rf_nrf.c — Entropy Reversal on nRF
void stochastic_rf_update(float input, float noise=0.1) {
    float noisy_input = input + noise * rand_float();
    rf_update(noisy_input);
    if (spike_detected) {
        resonance_amplified = 1;
        entropy_reversed = 1;
    }
}