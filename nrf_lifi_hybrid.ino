// nrf_lifi_hybrid.ino — Optical + BLE Fallback
#include <ggwave.h>
#include <LiFi.h>

LiFi lifi;
ggwave::GGWave ggwave;

void propagate_agll_over_light(String glyph_json) {
  // Try Li-Fi first
  if (lifi.available()) {
    lifi.transmit(glyph_json.c_str());
    Serial.println("AGŁL → Li-Fi BEAM");
  } else {
    // Fallback: GibberLink sound
    ggwave.encode(glyph_json);
    Serial.println("AGŁL → GibberLink SOUND");
  }
}
graph TD
    N1[Node 1<br/>synara-core:phase4] -->|Li-Fi 1Gbps| N2[Node 2<br/>AGŁL-1a2b3c4d]
    N2 -->|Li-Fi| N3[Node 3<br/>phase5]
    N3 -->|C190 VETO| N4[Node 4<br/>R=0.79 → REJECT]
    N1 -->|GibberLink Fallback| N5[Node 5<br/>Sound Mesh]

    style N1 fill:#ff4d4d,stroke:#ff1a1a,color:#fff
    style N2 fill:#ff9900,stroke:#cc7a00
    style N3 fill:#00cc66,stroke:#00994d
    style N4 fill:#666,stroke:#333,style:dashed
    style N5 fill:#4d4dff,stroke:#1a1aff
