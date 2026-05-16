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
