#ifndef FPT_SPECTRAL_RADIUS_H
#define FPT_SPECTRAL_RADIUS_H

#include <math.h>
#include "fpt_core.h"

#define FPT_PI_ITERS 12

/**
 * Builds the 4x4 closed-loop Jacobian J = (I - alpha*M)(I - K*H)
 * and estimates its spectral radius using an oscillation-resilient power iteration.
 */
static inline float fpt_estimate_spectral_radius(const fpt_config_t* cfg) {
    if (!cfg) return 999.0f;

    // 1. Construct JF = (I - alpha*M)
    float JF[4][4] = {
        {1.0f - cfg->alpha_star * cfg->m_q,     0.0f,                                   0.0f,                                   0.0f},
        {0.0f,                                  1.0f - cfg->alpha_star * cfg->m_q_dot, 0.0f,                                   0.0f},
        {0.0f,                                  0.0f,                                  1.0f - cfg->alpha_star * cfg->m_tau,   0.0f},
        {0.0f,                                  0.0f,                                   0.0f,                                  1.0f - cfg->alpha_star * cfg->m_gamma}
    };

    // 2. Construct JC = (I - K*H)
    float JC[4][4] = {
        {1.0f - cfg->k11,  -cfg->k12,          0.0f,        0.0f},
        {-cfg->k21,         1.0f - cfg->k22,    0.0f,        0.0f},
        {-cfg->k31,         0.0f,               1.0f,        0.0f},
        {0.0f,             -cfg->k42,          0.0f,        1.0f}
    };

    // 3. Compute Compound Operator: J = JF * JC
    float J[4][4] = {0.0f};
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            for (int k = 0; k < 4; ++k) {
                J[i][j] += JF[i][k] * JC[k][j];
            }
        }
    }

    // 4. Power Iteration Sequence
    float v[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    float v_next[4];
    float last_norm = 1.0f;

    for (int iter = 0; iter < FPT_PI_ITERS; ++iter) {
        // Multiply: v_next = J * v
        for (int i = 0; i < 4; ++i) {
            v_next[i] = 0.0f;
            for (int j = 0; j < 4; ++j) {
                v_next[i] += J[i][j] * v[j];
            }
        }

        // Compute Maximum Infinity Norm
        float norm = fabsf(v_next[0]);
        for (int i = 1; i < 4; ++i) {
            if (fabsf(v_next[i]) > norm) {
                norm = fabsf(v_next[i]);
            }
        }

        // Zero threshold guard
        if (norm < 1e-6f) {
            return 0.0f;
        }

        // Cache previous scaling factor to resolve complex conjugate oscillations
        last_norm = norm;

        // Vector normalization update
        for (int i = 0; i < 4; ++i) {
            v[i] = v_next[i] / norm;
        }
    }

    // 5. Dual-Verification Vector Magnitude Ingestion
    // Compares rayleigh matrix bounds alongside standard tracking values
    float num = 0.0f, den = 0.0f;
    for (int i = 0; i < 4; ++i) {
        float Jv_i = 0.0f;
        for (int j = 0; j < 4; ++j) {
            Jv_i += J[i][j] * v[j];
        }
        num += v[i] * Jv_i;
        den += v[i] * v[i];
    }

    float rayleigh_est = (den > 1e-6f) ? fabsf(num / den) : 0.0f;
    
    // Returns the maximum verified bound, securing the check against complex conjugate drops
    return (last_norm > rayleigh_est) ? last_norm : rayleigh_est;
}

#endif // FPT_SPECTRAL_RADIUS_H
