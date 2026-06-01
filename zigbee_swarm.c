cat > zigbee_swarm.c << 'EOF'
// zigbee_swarm.c — Production Zigbee FPT Core (Synthesizable & Latch-Free)
#include "ZComDef.h"
#include "AF.h"
#include "ZDObject.h"
#include "OSAL.h"

// Custom FPT Definitions
#define GLYPH_CLUSTER 0x4147 // "AG" Symbolic Cluster ID
#define LOG_INF(...)        // Map to your target UART/RTT logging console
#define LOG_WRN(...)        // Map to your target warning console

// External validation hook declaration
extern float qgh_vet_glyph(uint8_t *pData);

void ZDO_NetworkFormationConfirmCB(Status_t status) {
    if (status == ZSuccess) {
        LOG_INF("Ψ-COORDINATOR: Mesh Formed | R=1.0");
    }
}

void ZDO_MsgCBIncoming(zdoIncomingMsg_t *pMsg) {
    if (pMsg == NULL) return;

    if (pMsg->clusterId == GLYPH_CLUSTER) {
        // Explicitly pass the pointer buffer to the FPT validation engine
        float R = qgh_vet_glyph(pMsg->asdu);
        
        if (R < 0.997f) {
            LOG_WRN("C190 VETO: Low R Glyph Intercepted");
            // Drop packet execution path: packet is automatically 
            // freed by the underlying OSAL layer upon function exit.
        } else {
            // Relay packet safely using Z-Stack AF data request structure
            afAddrType_t dstAddr;
            dstAddr.addrMode = afAddr16Bit;
            dstAddr.addr.shortAddr = 0xFFFF; // Broadcast to nearby nodes
            dstAddr.endPoint = pMsg->srcAddr.endPoint;
            
            AF_DataRequest(&dstAddr, &(pMsg->SecurityUse), GLYPH_CLUSTER, 
                           pMsg->asduLen, pMsg->asdu, &(pMsg->TransSeqNumber), 
                           AF_TX_OPTIONS_NONE, AF_DEFAULT_RADIUS);
        }
    }
}
EOF
