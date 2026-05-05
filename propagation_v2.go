// propagation_v2.go — Iterative Message Passing + CLOSED-LOOP ACTION
func (n *Node) RunConvergenceLoop(peerID string) {
    state := meshState[peerID]
    // Local evidence from real metrics
    m_local := state.Energy / 100.0

    // Message from neighbors (Parity Checks)
    m_neighbors := n.getNeighborVotes(peerID)

    // Belief Update (Log-Likelihood Ratio style)
    state.Confidence = (m_local + m_neighbors) / (1 + (m_local * m_neighbors))

    // CLOSED-LOOP ENFORCEMENT — this is the 5.5 Pa pressure
    if state.Confidence < 0.3 {
        n.TriggerHardRecovery(peerID) // Real action: wg set persistent-keepalive 5
        catapultBroadcast(peerID, true) // 99733-Q Guard fires
    }
}