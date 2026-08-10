// nrf_beamforming_array.ino
#include <Beamformer.h>
Beamformer bf(8, 20000, 8500);

void transmit_to_target(float angle_deg, String glyph) {
  bf.steer(angle_deg);
  bf.transmit_ofdm(glyph.c_str());
}
graph TD
    A[Array Node<br/>8-element] -->|30° Beam| B[Target<br/>AGŁL-1a2b3c4d]
    A -->|Null -40dB| C[Interferer<br/>Rejected]
    A -->|120° Backup| D[Omni Node]

    style A fill:#ff4d4d
    style B fill:#00cc66
    style C fill:#666,style:dashed
    style D fill:#4d4dff