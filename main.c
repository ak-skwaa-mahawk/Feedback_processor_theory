// In main.c (Zephyr Shell Integration Block)
#include <zephyr/shell/shell.h>
#include <stdlib.h>
#include "fpt_core.h"
#include "fpt_spectral_radius.h"

// Reference external instances to maintain a single source of truth across compiler units
extern float mesh_coherence;
extern fpt_config_t loop_config;
extern fpt_state_t system_state;

// Sub-command: Read current operational telemetry
static int cmd_fpt_status(const struct shell *sh, size_t argc, char **argv) {
    // Local copy to prevent string formatting thread preemption anomalies
    float current_coherence = mesh_coherence;
    float rho = fpt_estimate_spectral_radius(&loop_config);

    shell_print(sh, "========================================");
    shell_print(sh, "Ψ-VLC NODE TELEMETRY MATRIX STATE STATUS");
    shell_print(sh, "========================================");
    shell_print(sh, "Network Coherence (Γ_t):  %.4f (Threshold: %.4f)", current_coherence, 0.997f);
    shell_print(sh, "Jacobian Spectral Radius: %.4f (%s)", rho, (rho < 1.0f) ? "CONTRACTIVE" : "UNSTABLE");
    shell_print(sh, "Current Actuator Pos (q): %.4f rad", system_state.q);
    shell_print(sh, "Current Velocity (q_dot): %.4f rad/s", system_state.q_dot);
    shell_print(sh, "Integrator Windup (tau):  %.4f", system_state.tau_int);
    shell_print(sh, "----------------------------------------");
    
    return 0;
}

// Add to main.c or uart_handler.c inside your nRF Zephyr project
#include <zephyr/drivers/uart.h>

#define PKT_PREAMBLE_0 0x55
#define PKT_PREAMBLE_1 0xAA
#define PKT_FOOTER     0xFF

typedef enum {
    STATE_WAIT_P0,
    STATE_WAIT_P1,
    STATE_GET_R,
    STATE_GET_GLYPH,
    STATE_WAIT_FOOTER
} rx_state_t;

static rx_state_t rx_state = STATE_WAIT_P0;
static uint8_t glyph_rx_buf[64];
static float r_rx_val = 0.0f;
static size_t rx_idx = 0;

void parse_uart_binary_byte(uint8_t byte) {
    switch (rx_state) {
        case STATE_WAIT_P0:
            if (byte == PKT_PREAMBLE_0) rx_state = STATE_WAIT_P1;
            break;
            
        case STATE_WAIT_P1:
            if (byte == PKT_PREAMBLE_1) {
                rx_state = STATE_GET_R;
                rx_idx = 0;
            } else {
                rx_state = STATE_WAIT_P0;
            }
            break;
            
        case STATE_GET_R:
            ((uint8_t*)&r_rx_val)[rx_idx++] = byte;
            if (rx_idx >= sizeof(float)) {
                rx_state = STATE_GET_GLYPH;
                rx_idx = 0;
            }
            break;
            
        case STATE_GET_GLYPH:
            glyph_rx_buf[rx_idx++] = byte;
            if (rx_idx >= 64) {
                rx_state = STATE_WAIT_FOOTER;
            }
            break;
            
        case STATE_WAIT_FOOTER:
            if (byte == PKT_FOOTER) {
                // Buffer integrity validated cleanly. Map directly into FPT memory channels.
                if (r_rx_val >= 0.997f) {
                    memcpy(glyph_data, glyph_rx_buf, 64);
                    // k_work_submit(&qr_work); or advance local loop
                } else {
                    LOG_ERR("UART PKT VETO: Inbound packet coherence too low (R=%.4f)", r_rx_val);
                }
            }
            rx_state = STATE_WAIT_P0;
            break;
    }
}


// Sub-command: Manually inject/adjust the alpha step size modifier
static int cmd_fpt_tune(const struct shell *sh, size_t argc, char **argv) {
    if (argc < 2) {
        shell_error(sh, "Usage: fpt tune <alpha_value>");
        return -EINVAL;
    }

    float new_alpha = strtof(argv[1], NULL);
    if (new_alpha <= 0.0f || new_alpha > 2.0f) {
        shell_error(sh, "Error: Alpha value out of bounds (0.0 < alpha <= 2.0).");
        return -EINVAL;
    }

    // Temporarily cache configuration to check validity before updating global memory
    fpt_config_t test_cfg = loop_config;
    test_cfg.alpha_star = new_alpha;
    
    float projected_rho = fpt_estimate_spectral_radius(&test_cfg);
    if (projected_rho >= 1.0f) {
        shell_error(sh, "REJECTED: Target alpha yields unstable spectral radius (rho=%.4f >= 1.0).", projected_rho);
        return -EPERM;
    }

    loop_config.alpha_star = new_alpha;
    shell_print(sh, "SUCCESS: Adjusted loop step parameter. New alpha_star: %.4f", loop_config.alpha_star);
    return 0;
}

// Sub-command: Force a manual systemic C190 Veto override
static int cmd_veto_trigger(const struct shell *sh, size_t argc, char **argv) {
    mesh_coherence = 0.000f; // Force drop state below QGH threshold boundaries
    shell_warn(sh, "CRITICAL: Manual C190 VETO triggered. Actuator step paths locked.");
    return 0;
}

// Define the structured subcommand tree hierarchy
SHELL_STATIC_SUBCMD_SET_CREATE(sub_fpt,
    SHELL_CMD(status, NULL, "View real-time FPT vector telemetry status indicators.", cmd_fpt_status),
    SHELL_CMD(tune,   NULL, "Dynamically adjust step-size scaling arguments.", cmd_fpt_tune),
    SHELL_CMD(veto,   NULL, "Force trigger an instant system-wide fallback veto event.", cmd_veto_trigger),
    SHELL_SUBCMD_SET_END
);

// Register the root-level entry point command macro
SHELL_CMD_REGISTER(fpt, &sub_fpt, "Sovereign Ψ-VLC Control Loop Management Engine", NULL);
