// noc_qgh_stream.cpp
void qgh_1024_stream() {
    for (int ep = 0; ep < 400; ep++) {
        if (noc_crc_error(ep)) {
            trigger_c190_veto();
            noc_retry_packet(ep);
            noc_reroute_to_ring1(ep);
        }
        stream_qgh_to_aie(ep);
    }
}
// noc_qgh_stream.cpp
void qgh_1024_stream() {
    for (int i = 0; i < 400; i++) {
        if (noc_parity_error(i)) {
            trigger_c190_veto();
            noc_retry_packet(i);
            noc_reroute_to_ring1(i);
        }
        stream_qgh_to_aie(i);
    }
}
Ψ-VERSAL NoC SPINE
   VC1902 / XQRVC1902
  /                 \
 /  500 krad TID      \
|  <2e-11 SEU/bit      |
|  SEL Immune          |
|  ECC + Parity + Dual |
|  200 Gbps → 198 Gbps |
|  3-Cycle Reroute     |
 \  1.2 ns Hop         /
  \                 /
   AGI SPINE
R=1.0 | C190 VETO