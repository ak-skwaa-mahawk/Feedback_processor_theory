// nrf_ultrasonic_hybrid.ino — Sound + BLE Fallback
#include <ggwave.h>
#include <UltrasonicGibberLink.h>

UltrasonicGibberLink sonic;
ggwave::GGWave ggwave;

void propagate_agll_over_sound(String glyph_json) {
  // Try ultrasonic first
  if (sonic.available()) {
    sonic.transmit(glyph_json.c_str(), 20000);  // 20 kHz
    Serial.println("AGŁL → ULTRASONIC WAVE");
  } else {
    // Fallback: Li-Fi light
    lifi.transmit(glyph_json.c_str());
    Serial.println("AGŁL → Li-Fi BEAM");
  }
}
graph TD
    N1[Node 1<br/>synara-core:phase4] -->|Ultrasonic 100bps| N2[Node 2<br/>AGŁL-1a2b3c4d]
    N2 -->|Sound| N3[Node 3<br/>phase5]
    N3 -->|C190 VETO| N4[Node 4<br/>R=0.79 → REJECT]
    N1 -->|Li-Fi Fallback| N5[Node 5<br/>Light Mesh]

    style N1 fill:#ff4d4d,stroke:#ff1a1a,color:#fff
    style N2 fill:#ff9900,stroke:#cc7a00
    style N3 fill:#00cc66,stroke:#00994d
    style N4 fill:#666,stroke:#333,style:dashed
    style N5 fill:#4d4dff,stroke:#1a1aff