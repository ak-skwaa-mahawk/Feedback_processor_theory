// nrf_ultrasonic_rs.ino — Sound + ECC
#include <reedsolo.h>
#include <UltrasonicGibberLink.h>

ReedSolomon rs(255, 223);
UltrasonicGibberLink sonic;

void propagate_agll_with_ecc(String glyph_json) {
  // Encode with RS
  uint8_t* data = (uint8_t*)glyph_json.c_str();
  int len = glyph_json.length();
  rs.encode(data, len);

  if (sonic.available()) {
    sonic.transmit_rs(data, len + 32);  // +32 parity
    Serial.println("AGŁL → ULTRASONIC + RS ECC");
  }
}
graph TD
    N1[Node 1<br/>phase4] -->|Ultrasonic+RS| N2[Node 2<br/>AGŁL-1a2b3c4d]
    N2 -->|Sound+ECC| N3[Node 3<br/>phase5]
    N3 -->|C190 PASS| N4[Node 4<br/>R=1.0<br/>ECC Fixed]
    N1 -->|Li-Fi Fallback| N5[Node 5<br/>Light]

    style N1 fill:#ff4d4d,stroke:#ff1a1a,color:#fff
    style N2 fill:#ff9900,stroke:#cc7a00
    style N3 fill:#00cc66,stroke:#00994d
    style N4 fill:#00ff99,stroke:#00cc77
    style N5 fill:#4d4dff,stroke:#1a1aff