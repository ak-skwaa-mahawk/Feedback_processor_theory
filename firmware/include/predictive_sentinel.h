#### firmware/include/predictive_sentinel.h
```c
// predictive_sentinel.h
#ifndef PREDICTIVE_SENTINEL_H
#define PREDICTIVE_SENTINEL_H

#include <stdint.h>
#include <stdbool.h>

#define SENTINEL_HISTORY_SIZE 1000
#define DRIFT_MODEL_ORDER 2  // Quadratic fit for acceleration detection

typedef struct {
    float baseline_buffer[SENTINEL_HISTORY_SIZE];
    float timestamp_buffer[SENTINEL_HISTORY_SIZE];
    uint16_t buffer_index;
    uint16_t buffer_count;
    
    // Drift model coefficients (ax² + bx + c)
    float drift_coeff_a;
    float drift_coeff_b;
    float drift_coeff_c;
    
    // Prediction state
    float predicted_failure_time;  // Hours from now
    float confidence_interval;     // ±this many hours
    bool failure_predicted;
    
    // Environmental context
    float temperature;
    float humidity;
} sentinel_state_t;

// Initialize sentinel
void sentinel_init(sentinel_state_t* sentinel);

// Update with new measurement
void sentinel_update(sentinel_state_t* sentinel, 
                     float measurement,
                     float temperature,
                     float humidity,
                     float timestamp);

// Predict time to failure (returns hours, or -1 if no failure predicted)
float sentinel_predict_failure(sentinel_state_t* sentinel);

// Get current drift rate (units per hour)
float sentinel_get_drift_rate(sentinel_state_t* sentinel);

// Detect anomaly (returns true if current reading is anomalous)
bool sentinel_detect_anomaly(sentinel_state_t* sentinel, 
                             float current_reading,
                             float threshold);

#endif // PREDICTIVE_SENTINEL_H