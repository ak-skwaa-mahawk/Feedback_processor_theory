// analog_rnn_nrf.c — Wave Resonance on nRF
void analog_rnn_step(float *input_seq) {
    float state = 0;
    for (int t = 0; t < seq_len; t++) {
        state = state + 0.7 * input_seq[t] - state*state*state;  // RF analog
        if (state > 1) trigger_resonance();
    }
}