#ifndef FPT_CORE_H
#define FPT_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define STATE_DIM 4
#define OBS_DIM   2

typedef struct {
    // Current System State Matrix Vector
    float q;
    float q_dot;
    float tau_int;
    float gamma_bias;
} fpt_state_t;

typedef struct {
    // Reference Targets (Vault Anchors)
    float q_target;
    float q_dot_target;
} fpt_reference_t;

typedef struct {
    // Linear Telemetry Feedback Gains (K Matrix Elements)
    float k11; float k12;
    float k21; float k22;
    float k31;
    float k42;

    // Vault Floor Energy Curvature Metrics (M Hessian Diagonals)
    float m_q;
    float m_q_dot;
    float m_tau;
    float m_gamma;

    // Vault-Gated Attenuation Step Size
    float alpha_star;
} fpt_config_t;

/**
 * Computes single-pass internal state stability metrics based on local Jacobian parameters.
 * Validates tracking compliance thresholds over isolated structural axis elements.
 */
static inline bool verify_fpt_contraction(const fpt_config_t* cfg) {
    if (!cfg) return false;

    float axis_q     = (1.0f - (cfg->alpha_star * cfg->m_q)) * (1.0f - cfg->k11);
    float axis_q_dot = (1.0f - (cfg->alpha_star * cfg->m_q_dot)) * (1.0f - cfg->k22);
    float axis_tau   = (1.0f - (cfg->alpha_star * cfg->m_tau));
    float axis_gamma = (1.0f - (cfg->alpha_star * cfg->m_gamma));

    return (fabsf(axis_q) < 1.0f) && 
           (fabsf(axis_q_dot) < 1.0f) && 
           (fabsf(axis_tau) < 1.0f) && 
           (fabsf(axis_gamma) < 1.0f);
}

/**
 * Executes a single complete FPT Loop Step: Observe -> Feedback -> Floor Projection
 * Mutates state parameters directly in memory according to geometric constraints.
 */
static inline void execute_fpt_crank(fpt_state_t* state, 
                                     const fpt_reference_t* ref, 
                                     const fpt_config_t* cfg) {
    if (!state || !ref || !cfg) return;

    // 1. Telemetry Observation Processing Loop (H Matrix Ingestion)
    float o_q = state->q;
    float o_q_dot = state->q_dot;

    // 2. Compute Tracking Deviations
    float error_q = ref->q_target - o_q;
    float error_q_dot = ref->q_dot_target - o_q_dot;

    // 3. Execute Linearized Feedback Correction Operator Step (C-Step)
    float tilde_q          = state->q          + (cfg->k11 * error_q) + (cfg->k12 * error_q_dot);
    float tilde_q_dot      = state->q_dot      + (cfg->k21 * error_q) + (cfg->k22 * error_q_dot);
    float tilde_tau_int    = state->tau_int    + (cfg->k31 * error_q);
    float tilde_gamma_bias = state->gamma_bias + (cfg->k42 * error_q_dot);

    // 4. Compute Energy Gradient Map Elements over Interpolated Post-Correction State Matrix
    float grad_E_q     = cfg->m_q     * (tilde_q - ref->q_target);
    float grad_E_q_dot = cfg->m_q_dot * (tilde_q_dot - ref->q_dot_target);
    float grad_E_tau   = cfg->m_tau   * tilde_tau_int; // Target structural minimum approaches zero
    float grad_E_gamma = cfg->m_gamma * tilde_gamma_bias;

    // 5. Vault Gated Floor Step Projection (Iterative Descent Realization)
    state->q          = tilde_q          - (cfg->alpha_star * grad_E_q);
    state->q_dot      = tilde_q_dot      - (cfg->alpha_star * grad_E_q_dot);
    state->tau_int    = tilde_tau_int    - (cfg->alpha_star * grad_E_tau);
    state->gamma_bias = tilde_gamma_bias - (cfg->alpha_star * grad_E_gamma);
}

#endif // FPT_CORE_H
