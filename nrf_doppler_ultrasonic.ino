// nrf_doppler_ultrasonic.ino
#include <DopplerCompensator.h>
#include <reedsolo.h>

DopplerCompensator doppler;
ReedSolomon rs(255, 223);

void propagate_in_motion(String glyph) {
  float shift = doppler.estimate_from_pilot();
  doppler.compensate(shift);
  rs.encode((uint8_t*)glyph.c_str(), glyph.length());
  sonic.transmit_rs compensated_data;
}
graph LR
    N1[Drone 1<br/>80 km/h →] -->|Ultrasonic+Doppler| N2[Drone 2<br/>AGŁL-1a2b3c4d]
    N2 -->|Motion| N3[Ground Node<br/>R=1.0]
    N1 -->|Li-Fi| N4[Backup]

    style N1 fill:#ff4d4d,stroke:#ff1a1a
    style N2 fill:#ff9900,stroke:#cc7a00
    style N3 fill:#00cc66,stroke:#00994d
    style N4 fill:#4d4dff,stroke:#1a1aff