// nrf_adaptive_beamformer.ino
#include <AdaptiveBeamformer.h>
AdaptiveBeamformer bf(8, 20000);

void lock_on_target(float known_angle) {
  bf.set_reference_pilot();
  bf.run_mvdr();  // or lms_update()
  bf.apply_weights();
  bf.transmit_ofdm_glyph();
}
graph TD
    A[Adaptive Array<br/>8-element] -->|MVDR 35°| T[Target<br/>AGŁL-1a2b3c4d]
    A -->|Null -45dB| I[Interferer<br/>Rejected]
    A -->|LMS Track| M[Moving Node]

    style A fill:#ff4d4d
    style T fill:#00cc66
    style I fill:#666,style:dashed
    style M fill:#ff9900