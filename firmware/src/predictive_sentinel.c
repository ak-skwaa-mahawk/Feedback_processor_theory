#include "predictive_sentinel.h"
#include <math.h>
#include <string.h>

// Least-squares polynomial fit (Vandermonde method)
static void fit_quadratic(const float* x, const float* y, uint16_t n,
                         float* a, float* b, float* c) {
    // Simplified 2nd-order fit for embedded (no matrix inverse)
    // Uses recursive least squares for efficiency
    
    float sum_x = 0, sum_x2 = 0, sum_x3 = 0, sum_x4 = 0;
    float sum_y = 0, sum_xy = 0, sum_x2y = 0;
    
    for (uint16_t i = 0; i < n; i++) {
        float xi = x[i];
        float yi = y[i];
        float xi2 = xi * xi;
        float xi3 = xi2 * xi;
        float xi4 = xi2 * xi2;
        
        sum_x += xi;
        sum_x2 += xi2;
        sum_x3 += xi3;
        sum_x4 += xi4;
        sum_y += yi;
        sum_xy += xi * yi;
        sum_x2y += xi2 * yi;
    }
    
    // Solve 3x3 system (Cramer's rule for embedded efficiency)
    float denom = n * (sum_x2 * sum_x4 - sum_x3 * sum_x3) 
                - sum_x * (sum_x * sum_x4 - sum_x2 * sum_x3)
                + sum_x2 * (sum_x * sum_x3 - sum_x2 * sum_x2);
    
    if (fabsf(denom) < 1e-10f) {
        // Singular matrix - fallback to linear
        *a = 0.0f;
        *b = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
        *c = (sum_y - (*b) * sum_x) / n;
        return;
    }
    
    *a = (n * (sum_x2y * sum_x4 - sum_x3 * sum_x2y) 
         - sum_y * (sum_x * sum_x4 - sum_x2 * sum_x3)
         + sum_xy * (sum_x * sum_x3 - sum_x2 * sum_x2)) / denom;
         
    *b = (n * (sum_x2 * sum_x2y - sum_x3 * sum_xy)
         - sum_x * (sum_x * sum_x2y - sum_x2 * sum_xy)
         + sum_x2 * (sum_x * sum_xy - sum_x2 * sum_y)) / denom;
         
    *c = (sum_y - (*b) * sum_x - (*a) * sum_x2) / n;
}

void sentinel_init(sentinel_state_t* sentinel) {
    memset(sentinel, 0, sizeof(sentinel_state_t));
    sentinel->buffer_index = 0;
    sentinel->buffer_count = 0;
    sentinel->predicted_failure_time = -1.0f;
    sentinel->failure_predicted = false;
}

void sentinel_update(sentinel_state_t* sentinel,
                    float measurement,
                    float temperature,
                    float humidity,
                    float timestamp) {
    // Circular buffer update
    sentinel->baseline_buffer[sentinel->buffer_index] = measurement;
    sentinel->timestamp_buffer[sentinel->buffer_index] = timestamp;
    
    sentinel->buffer_index = (sentinel->buffer_index + 1) % SENTINEL_HISTORY_SIZE;
    if (sentinel->buffer_count < SENTINEL_HISTORY_SIZE) {
        sentinel->buffer_count++;
    }
    
    // Store environmental context
    sentinel->temperature = temperature;
    sentinel->humidity = humidity;
    
    // Retrain drift model every 100 samples
    if (sentinel->buffer_count >= 100 && sentinel->buffer_count % 100 == 0) {
        // Normalize timestamps to hours from first sample
        float t0 = sentinel->timestamp_buffer[0];
        float normalized_times[SENTINEL_HISTORY_SIZE];
        
        for (uint16_t i = 0; i < sentinel->buffer_count; i++) {
            normalized_times[i] = (sentinel->timestamp_buffer[i] - t0) / 3600.0f;
        }
        
        fit_quadratic(normalized_times, 
                     sentinel->baseline_buffer,
                     sentinel->buffer_count,
                     &sentinel->drift_coeff_a,
                     &sentinel->drift_coeff_b,
                     &sentinel->drift_coeff_c);
    }
}

float sentinel_predict_failure(sentinel_state_t* sentinel) {
    if (sentinel->buffer_count < 100) {
        return -1.0f;  // Insufficient data
    }
    
    // Current time (normalized to hours)
    float t_now = (sentinel->timestamp_buffer[(sentinel->buffer_index - 1 + SENTINEL_HISTORY_SIZE) 
                                              % SENTINEL_HISTORY_SIZE]
                  - sentinel->timestamp_buffer[0]) / 3600.0f;
    
    // Current baseline value
    float baseline_now = sentinel->drift_coeff_a * t_now * t_now
                       + sentinel->drift_coeff_b * t_now
                       + sentinel->drift_coeff_c;
    
    // Failure threshold (20% deviation from initial baseline)
    float failure_threshold = 1.2f * sentinel->drift_coeff_c;
    
    // Solve quadratic: a*t² + b*t + (c - threshold) = 0
    float a = sentinel->drift_coeff_a;
    float b = sentinel->drift_coeff_b;
    float c = sentinel->drift_coeff_c - failure_threshold;
    
    float discriminant = b * b - 4.0f * a * c;
    
    if (discriminant < 0 || fabsf(a) < 1e-10f) {
        // No real roots or nearly linear - check linear case
        if (fabsf(b) > 1e-10f) {
            float t_fail = -c / b;
            if (t_fail > t_now) {
                sentinel->predicted_failure_time = t_fail - t_now;
                sentinel->failure_predicted = true;
                return sentinel->predicted_failure_time;
            }
        }
        sentinel->failure_predicted = false;
        return -1.0f;
    }
    
    // Two roots - take the positive one > t_now
    float sqrt_disc = sqrtf(discriminant);
    float t1 = (-b + sqrt_disc) / (2.0f * a);
    float t2 = (-b - sqrt_disc) / (2.0f * a);
    
    float t_fail = (t1 > t_now) ? t1 : ((t2 > t_now) ? t2 : -1.0f);
    
    if (t_fail > t_now) {
        sentinel->predicted_failure_time = t_fail - t_now;
        sentinel->failure_predicted = true;
        
        // Confidence interval (simple: ±10% of prediction time)
        sentinel->confidence_interval = 0.1f * sentinel->predicted_failure_time;
        
        return sentinel->predicted_failure_time;
    }
    
    sentinel->failure_predicted = false;
    return -1.0f;
}

float sentinel_get_drift_rate(sentinel_state_t* sentinel) {
    if (sentinel->buffer_count < 10) {
        return 0.0f;
    }
    
    // Current time
    float t_now = (sentinel->timestamp_buffer[(sentinel->buffer_index - 1 + SENTINEL_HISTORY_SIZE)
                                              % SENTINEL_HISTORY_SIZE]
                  - sentinel->timestamp_buffer[0]) / 3600.0f;
    
    // Derivative: 2*a*t + b
    return 2.0f * sentinel->drift_coeff_a * t_now + sentinel->drift_coeff_b;
}

bool sentinel_detect_anomaly(sentinel_state_t* sentinel,
                             float current_reading,
                             float threshold) {
    if (sentinel->buffer_count < 10) {
        return false;  // Need baseline first
    }
    
    // Expected value at current time
    float t_now = (sentinel->timestamp_buffer[(sentinel->buffer_index - 1 + SENTINEL_HISTORY_SIZE)
                                              % SENTINEL_HISTORY_SIZE]
                  - sentinel->timestamp_buffer[0]) / 3600.0f;
    
    float expected = sentinel->drift_coeff_a * t_now * t_now
                   + sentinel->drift_coeff_b * t_now
                   + sentinel->drift_coeff_c;
    
    // Deviation
    float deviation = fabsf(current_reading - expected) / expected;
    
    return (deviation > threshold);
}
// In aie_tmr_reg.c
#include "predictive_sentinel.h"

static sentinel_state_t sentinel_rx[4];  // One per RX channel
static sentinel_state_t sentinel_tx[4];  // One per TX channel

void tmr_update_with_prediction(void) {
    // Read channels
    float rx_readings[4];
    for (int i = 0; i < 4; i++) {
        rx_readings[i] = aie_read_rx_channel(i);
    }
    
    // Update sentinels
    float timestamp = get_system_time();
    float temp = read_temperature();
    float humidity = read_humidity();
    
    for (int i = 0; i < 4; i++) {
        sentinel_update(&sentinel_rx[i], rx_readings[i], temp, humidity, timestamp);
        
        // Check for predicted failures
        float ttf = sentinel_predict_failure(&sentinel_rx[i]);
        if (ttf > 0 && ttf < 168.0f) {  // Less than 1 week
            log_warning("RX channel %d: Predicted failure in %.1f hours", i, ttf);
            schedule_maintenance(i, ttf);
        }
        
        // Anomaly detection
        if (sentinel_detect_anomaly(&sentinel_rx[i], rx_readings[i], 0.05f)) {
            log_alert("RX channel %d: Anomaly detected (%.3f deviation)", 
                     i, rx_readings[i]);
        }
    }
    
    // TMR voting with sentinel weighting
    float weighted_avg = 0.0f;
    float weight_sum = 0.0f;
    
    for (int i = 0; i < 3; i++) {  // Only active channels (not sentinel)
        float drift_rate = sentinel_get_drift_rate(&sentinel_rx[i]);
        float weight = 1.0f / (1.0f + fabsf(drift_rate));  // Lower weight for drifting channels
        
        weighted_avg += weight * rx_readings[i];
        weight_sum += weight;
    }
    
    float consensus = weighted_avg / weight_sum;
    
    // Validate against sentinel (channel 3)
    if (sentinel_detect_anomaly(&sentinel_rx[3], consensus, 0.05f)) {
        log_warning("Consensus value anomalous per sentinel - all channels may be drifting");
        // Trigger recalibration
        recalibrate_all_channels();
    }
}
// Coordination: Choose patterns, enforce constraints, track state
float coordinate_sensor_patterns(rx_data_t* rx_channels) {
    // 1. Weighted vote (choose reliable patterns)
    float consensus = tmr_weighted_vote(rx_channels, drift_weights);
    
    // 2. Sentinel constraint enforcement
    if (!sentinel_validates(consensus, rx_sentinel)) {
        recalibrate_baseline();  // Anchor too weak
        return NAN;  // Reject
    }
    
    // 3. State tracking via FSM (rtl/power_fsm.v integration)
    switch(power_state) {  // From pid_fpt.v PID control
        case SURVEILLANCE: monitor_passively(); break;
        case ALERT: increase_scan_rate(); break;  // Threshold ~0.7 anchoring
        case ATTACK: coordinate_swarm_response(); break;
    }
    return consensus;
}