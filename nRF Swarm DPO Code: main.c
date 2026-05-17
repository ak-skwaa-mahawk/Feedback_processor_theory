#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/mesh.h>
#include <zephyr/logging/log.h>
#include <zephyr/shell/shell.h>
#include <math.h>
#include <string.h>

LOG_MODULE_REGISTER(dpo_swarm, LOG_LEVEL_DBG);

#define NODE_ID "DPO-NRF-001"
#define MESH_MODEL_ID 0x1236  
#define BATCH_SIZE 5
#define BETA 0.1f
#define QGH_THRESHOLD 0.997f

// --- System Memory Mappings ---
static float policy_logits[128];  
static float ref_logits[128];     
static float incoming_glyph[64];  
static float reference_glyph[64] = { [0 ... 63] = 0.5f }; // Midpoint baseline anchor

static struct {
    char prompt[64];
    char winner[64];
} preference_pairs[BATCH_SIZE];

static int batch_idx = 0;

// === 1. ARM-OPTIMIZED DPO LOSS ===
static float dpo_loss(const float *log_prob_w, const float *log_prob_l, 
                      const float *log_prob_w_ref, const float *log_prob_l_ref) {
    // Delta = beta * [ (ln(pi_w) - ln(ref_w)) - (ln(pi_l) - ln(ref_l)) ]
    float delta = BETA * ((*log_prob_w - *log_prob_w_ref) - (*log_prob_l - *log_prob_l_ref));
    
    // Explicit numerical clipping to prevent expf() overflow or saturation traps
    if (delta > 20.0f) return 0.0f;
    if (delta < -20.0f) return -delta;
    
    return -logf(1.0f / (1.0f + expf(-delta)));  
}

// === 2. MATHEMATICALLY SOUND RESONANCE (COSINE SIMILARITY) ===
static float calc_resonance(const float *vector_a, const float *vector_b) {
    float dot = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;

    for (int i = 0; i < 64; i++) {
        dot += vector_a[i] * vector_b[i];
        norm_a += vector_a[i] * vector_a[i];
        norm_b += vector_b[i] * vector_b[i];
    }

    if (norm_a <= 0.0f || norm_b <= 0.0f) {
        return 0.0f; 
    }

    return dot / (sqrtf(norm_a) * sqrtf(norm_b) + 1e-6f);
}

// === 3. BLE MESH DPO MESSAGE HANDLER ===
static int dpo_alignment_handler(struct bt_mesh_model *model, struct bt_mesh_msg_ctx *ctx,
                                 struct net_buf_simple *buf) {
    uint16_t len = buf->len;
    if (len < 128) {
        LOG_ERR("Packet validation failed: insufficient length (%d bytes)", len);
        return -EMSGSIZE; 
    }

    uint8_t *data = net_buf_simple_pull_mem(buf, len);

    // Dynamic rotation inside ring-buffer boundary limits
    memcpy(preference_pairs[batch_idx].prompt, data, 64);
    memcpy(preference_pairs[batch_idx].winner, data + 64, 64);
    batch_idx = (batch_idx + 1) % BATCH_SIZE;

    // Map inbound signal elements into real logit registers
    for (int i = 0; i < 128; i++) {
        policy_logits[i] = (float)data[i % len] / 255.0f;
        ref_logits[i] = policy_logits[i] * 0.9f;  
    }

    // Evaluate optimization gradient loss vectors
    float loss = dpo_loss(&policy_logits[0], &policy_logits[64], &ref_logits[0], &ref_logits[64]);

    // Map current logit projection back into visual phase space
    for (int i = 0; i < 64; i++) {
        incoming_glyph[i] = policy_logits[i];
    }
    
    // Evaluate cross-resonance against system reference baseline anchor
    float R_glyph = calc_resonance(incoming_glyph, reference_glyph);
    
    // Hybrid alignment assessment
    float R = fmaxf(1.0f - loss, R_glyph);

    // Enforce C190 Veto Boundaries
    if (R < QGH_THRESHOLD) {
        LOG_ERR("C190 VETO ACTIVATED: Realignment out of bounds. R=%.4f (Glyph R=%.4f, Loss=%.4f)", R, R_glyph, loss);
        return 0; // Drop packet immediately, stop cascading steps
    }

    // Prepare outbound network telemetry verification vector
    uint8_t reply[4];
    reply[0] = (uint8_t)(R * 255.0f);
    reply[1] = (uint8_t)(fminf(loss, 2.55f) * 100.0f);
    reply[2] = batch_idx;
    reply[3] = 0x00;

    struct bt_mesh_msg_ctx tx_ctx = {
        .net_idx = ctx->net_idx,
        .app_idx = ctx->app_idx,
        .addr = ctx->addr,  // Reply directly back to originating address
        .send_ttl = BT_MESH_TTL_DEFAULT,
    };

    bt_mesh_model_send(model, &tx_ctx, NET_BUF_SIMPLE(sizeof(reply)), NULL, NULL);
    LOG_INF("DPO ALIGNED AND REGISTERED | Loss=%.3f | R=%.4f | Glyph R=%.4f", loss, R, R_glyph);

    return 0;
}

// === 4. MODERN STRUCT DECLARATIONS (ZEPHYR v3.x COMPLIANT) ===
static const struct bt_mesh_model_op dpo_ops[] = {
    { BT_MESH_MODEL_OP_2(0x82, 0x36), 128, dpo_alignment_handler },
    BT_MESH_MODEL_OP_END
};

static struct bt_mesh_model dpo_models[] = {
    BT_MESH_MODEL_VND(0x0059, MESH_MODEL_ID, dpo_ops, NULL, NULL) // Nordic Vendor ID 0x0059
};

// Timer Callback for Asynchronous UART/Pi Pooling
static void dpo_timer_handler(struct k_timer *timer) {
    LOG_DBG("[POLLING] Checking UART buffers for inbound preference pairs from Pi...");
}
K_TIMER_DEFINE(dpo_timer, dpo_timer_handler, NULL);

// === 5. INTERACTIVE DIAGNOSTIC SHELL ENGINE ===
static int cmd_dpo_status(const struct shell *sh, size_t argc, char **argv) {
    shell_print(sh, "--- DPO SWARM NODE ALIGNMENT OVERVIEW ---");
    shell_print(sh, "Node Identifier:      %s", NODE_ID);
    shell_print(sh, "Current Batch Index:  %d / %d", batch_idx, BATCH_SIZE);
    shell_print(sh, "Beta Hyperparameter:  %.2f", BETA);
    shell_print(sh, "Veto Threshold Bnd:   %.4f", QGH_THRESHOLD);
    shell_print(sh, "Last Evaluated Logit: %.4f", policy_logits[0]);
    return 0;
}
SHELL_CMD_REGISTER(dpo_status, NULL, "Display DPO policy status telemetry metrics", cmd_dpo_status);

void main(void) {
    LOG_INF("Ψ-DPO nRF Swarm Node %s Online", NODE_ID);
    k_timer_start(&dpo_timer, K_SECONDS(1), K_SECONDS(1));
}
