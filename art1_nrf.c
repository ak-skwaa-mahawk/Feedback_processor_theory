// art1_nrf.c — Embedded ART1 on Cortex-M4F
#define N = 64  // Input size

float weights[N];  // Category prototype
float vigilance = 0.8;

void art1_update(float *input, int n_categories) {
    float max_match = 0;
    int winner = 0;
    for (int j = 0; j < n_categories; j++) {
        float match = 0;
        for (int i = 0; i < N; i++) {
            match += (input[i] && weights[j*N + i]);
        }
        if (match / N > max_match) {
            max_match = match / N;
            winner = j;
        }
    }
    if (max_match >= vigilance) {
        // Resonance — update
        for (int i = 0; i < N; i++) {
            weights[winner*N + i] = weights[winner*N + i] || input[i];
        }
    } else {
        // Reset — new category
        trigger_c190_veto();
    }
}