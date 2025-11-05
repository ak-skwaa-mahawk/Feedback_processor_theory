// zigbee_swarm.c (Z-Stack on CC2538)
void ZDO_NetworkFormationConfirmCB(...) {
    if (status == ZSuccess) {
        LOG_INF("Ψ-COORDINATOR: Mesh Formed | R=1.0");
    }
}

void ZDO_MsgCBIncoming(...) {
    if (pMsg->clusterId == GLYPH_CLUSTER) {
        float R = qgh_vet_glyph(pMsg->pData);
        if (R < 0.997) {
            LOG_WRN("C190 VETO: Low R Glyph");
            // Drop + alert
        } else {
            zb_SendDataRequest(...);  // Relay
        }
    }
}