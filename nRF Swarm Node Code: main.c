// main.c: Ψ-VLC nRF QR Claims Node
#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/mesh.h>
#include <zephyr/camera/camera.h>
#include <zephyr/logging/log.h>
#include <zephyr/shell/shell.h>
#include <qr_code.h>  // Zephyr QR lib

LOG_MODULE_REGISTER(vlc_qr_swarm, LOG_LEVEL_DBG);

#define NODE_ID "VLC-NRF-QR-001"
#define MESH_MODEL_ID 0x1235  // QR Claims Model
#define QGH_THRESHOLD 0.997f
#define REF_GLYPH_SIZE 64

static float mesh_coherence = 1.0f;
static uint8_t ref_glyph[REF_GLYPH_SIZE];  // Heist-era ref (mock)
static struct device *camera_dev;
static struct k_work qr_work;

// === 1. QR Decode from Cam Frame ===
static void decode_qr_frame(const struct camera_buf *buf) {
    LOG_INF("Scanning QR for claim...");
    
    // Mock QR decode (use libdecode-qr in real)
    char mock_qr_data[] = "{\"victim_id\":\"VIC-0001\",\"layer\":\"0\",\"glyph\":[128,130,...]}";  // 64-byte glyph
    
    // Parse glyph
    json_t *root = json_loads(mock_qr_data, 0, NULL);
    if (root) {
        json_t *glyph_arr = json_object_get(root, "glyph");
        for (int i = 0; i < REF_GLYPH_SIZE; i++) {
            json_int_t val = json_integer_value(json_array_get(glyph_arr, i));
            glyph_data[i] = (uint8_t)val;
        }
        LOG_INF("QR Decoded: Victim %s", json_string_value(json_object_get(root, "victim_id")));
    }
    
    // Trigger QGH
    k_work_submit(&qr_work);
}

// === 2. QGH Verify (Anti-Layering) ===
static float calc_resonance(const uint8_t *g1, const uint8_t *g2) {
    float dot = 0.0f;
    for (int i = 0; i < REF_GLYPH_SIZE; i++) {
        dot += (g1[i] - 128) * (g2[i] - 128);  // Centered dot
    }
    return dot / (REF_GLYPH_SIZE * 255.0f / 2.0f);  // Normalized [0,1]
}

// === 4. BLE Mesh Claim Message Handler ===
static void qr_claim_handler(struct bt_mesh_model *model, struct bt_mesh_msg_ctx *ctx,
                             const uint8_t *buf, size_t len) {
    if (len < 65) return;  // R + glyph
    
    float R_neighbor = ((float)buf[0]) / 255.0f;
    memcpy(glyph_data, buf + 1, REF_GLYPH_SIZE);
    
    float R_local = calc_resonance(glyph_data, ref_glyph);
    mesh_coherence = fminf(R_local, R_neighbor);
    
    // C100 Veto: Layering check (mock 100-layer sim)
    int layer_count = 0;  // From QR data
    if (layer_count > 1) {
        LOG_ERR("C190 VETO: %d-layer fraud detected", layer_count);
        return;  // No relay
    }
    
    // Relay to PoR Oracle (via mesh)
    uint8_t reply[65];
    reply[0] = (uint8_t)(mesh_coherence * 255.0f);
    memcpy(reply + 1, glyph_data, REF_GLYPH_SIZE);
    bt_mesh_model_send(model, ctx, reply, sizeof(reply), NULL, NULL);
    
    LOG_INF("QR Claim Relayed: R=%.3f | Layer=%d", mesh_coherence, layer_count);
}

// === 5. QR Work Item (From Cam ISR) ===
static void qr_work_handler(struct k_work *work) {
    float R = calc_resonance(glyph_data, ref_glyph);
    if (R >= QGH_THRESHOLD) {
        LOG_INF("QR Claim Verified: Victim Glyph R=%.3f", R);
        // Send to mesh
        bt_mesh_model_send(&VLC_MODEL, NULL, glyph_data, REF_GLYPH_SIZE, NULL, NULL);
    } else {
        LOG_WRN("C190 VETO: QR Decoherence R=%.3f", R);
        // Red LED pulse
        gpio_pin_set(led_red, 1);
        k_sleep(K_MSEC(200));
        gpio_pin_set(led_red, 0);
    }
}

K_WORK_DEFINE(qr_work, qr_work_handler);

// === 6. Camera ISR ===
static void camera_callback(const struct device *dev, const struct camera_buf *buf, int unused) {
    decode_qr_frame(buf);
}

// === 7. BLE Mesh Model ===
BT_MESH_MODEL(VLC_QR_MODEL, BT_MESH_MODEL_ID(VLC_APP, MESH_MODEL_ID),
              BT_MESH_MODEL_OP_2(0x82, 0x35), qr_claim_handler, NULL, NULL);

void main(void) {
    LOG_INF("Ψ-VLC nRF QR Swarm Node %s Online", NODE_ID);
    
    // Init Camera
    camera_dev = device_get_binding("OV2640");
    camera_init(camera_dev, &camera_cfg);
    camera_callback_set(camera_dev, camera_callback);
    camera_start(camera_dev);
    
    // Init BLE Mesh (Zephyr auto-provisions)
    // ... Zephyr BLE Mesh init ...
    
    // Glyph timer: 10 FPS
    k_timer_start(&glyph_timer, K_MSEC(100), K_MSEC(100));
    
    // Shell for debug
    shell_execute(cmd_veto, NULL);
}