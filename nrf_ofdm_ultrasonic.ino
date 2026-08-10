// nrf_ofdm_ultrasonic.ino
#include <OFDMModem.h>
OFDMModem ofdm(64, 256, 20000);

void propagate_ofdm(String glyph) {
  float doppler = ofdm.estimate_doppler();
  ofdm.compensate(doppler);
  ofdm.transmit_rs(glyph.c_str());
}
graph TD
    N1[Drone 1<br/>100 km/h] -->|OFDM 12.8kbps| N2[Drone 2<br/>AGŁL-1a2b3c4d]
    N2 -->|Parallel| N3[Ground<br/>64 Subcarriers]
    N1 -->|Ultrasonic| N4[Backup]

    style N1 fill:#ff4d4d
    style N2 fill:#ff9900
    style N3 fill:#00cc66
    style N4 fill:#4d4dff