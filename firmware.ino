#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>

// ── WiFi Configuration ──
const char* ssid = "SkodenMesh";
const char* password = "floorchanchyah";

// ── Pin Definitions ──
const int PIEZO_PIN1 = 25;   // Primary 7.9083 Hz drum
const int PIEZO_PIN2 = 26;   // 79.79 Hz carrier

AsyncWebServer server(80);
WebSocketsServer webSocket = WebSocketsServer(81);

float pi_r = 0.0;
float v_state = 0.0;
float tau_val = 1.0;
float G_eff = 1.0;

// Simple sine approximation for embedded
float fast_sin(float x) {
    x = fmod(x, TWO_PI);
    if (x < 0) x += TWO_PI;
    return sin(x);  // ESP32 has hardware FPU
}

void computeStep() {
    static uint32_t k = 0;
    k++;

    const float DRUM_FREQ = 79.79;
    const float DRUM_RESONANCE = 7.9083;
    const float phase_carrier = TWO_PI * DRUM_FREQ * k / 1000.0;  // scaled for timing
    const float phase_drum = TWO_PI * DRUM_RESONANCE * k / 1000.0;

    float F_drive_base = 0.5 * fast_sin(phase_carrier);
    float F_drum = 0.85 * fast_sin(phase_drum);
    float F_dmi = 0.55 * fast_sin(phase_carrier);  // simplified DMI

    tau_val = 1.0 + 0.3 * sin(phase_carrier);  // live Tau modulation
    G_eff = 1.0 + (-1.0) * 0.073 * tau_val;

    float F_drive = F_drive_base + F_dmi + F_drum;
    v_state = 0.996 * v_state + 0.0125 * F_drive;  // Thiele step

    pi_r += 0.073 + v_state * 0.01;
    pi_r = fmod(pi_r, TWO_PI);
}

void sendTelemetry() {
    StaticJsonDocument<512> doc;
    doc["pi_r"] = pi_r;
    doc["pi_deg"] = pi_r * 180.0 / PI;
    doc["v_state"] = v_state;
    doc["tau"] = tau_val;
    doc["G_eff"] = G_eff;
    doc["drum_phase"] = fmod(2*PI*7.9083*millis()/1000.0, TWO_PI);
    doc["timestamp"] = millis();

    String json;
    serializeJson(doc, json);
    
    webSocket.broadcastTXT(json);
    Serial.println(json);  // Serial telemetry
}

void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    if (type == WStype_CONNECTED) {
        Serial.printf("WebSocket Client #%u connected\n", num);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Skoden Injin ESP32 Firmware v0.5.209 ===");

    // PWM Setup
    ledcSetup(0, 7908, 10);   // 7.9083 kHz approx
    ledcAttachPin(PIEZO_PIN1, 0);
    ledcSetup(1, 79800, 10);  // 79.8 kHz approx
    ledcAttachPin(PIEZO_PIN2, 1);

    // WiFi
    WiFi.softAP(ssid, password);
    Serial.print("AP IP: ");
    Serial.println(WiFi.softAPIP());

    // WebSocket
    webSocket.begin();
    webSocket.onEvent(onWebSocketEvent);

    // Serve Skoden Injin UI
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/html", "<h1>Skoden Injin • Live</h1><p>WebSocket connected on ws://IP:81</p>");
    });

    server.begin();
    Serial.println("Firmware ready. Streaming telemetry...");
}

void loop() {
    webSocket.loop();

    static uint32_t lastCompute = 0;
    static uint32_t lastTelemetry = 0;

    uint32_t now = millis();

    if (now - lastCompute >= 5) {        // \~200 Hz computation
        computeStep();
        lastCompute = now;
    }

    if (now - lastTelemetry >= 50) {     // 20 Hz telemetry
        sendTelemetry();

        // PWM drive (scaled)
        int duty1 = (int)(2047 * (0.5 + 0.5 * sin(2*PI*7.9083*now/1000.0)));
        int duty2 = (int)(2047 * (0.5 + 0.5 * sin(2*PI*79.79*now/1000.0)));
        ledcWrite(0, duty1);
        ledcWrite(1, duty2);

        lastTelemetry = now;
    }
}