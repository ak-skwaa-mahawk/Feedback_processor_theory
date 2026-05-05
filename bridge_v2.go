// bridge_v2.go — The Soliton Telemetry Exporter
func (n *Node) ExportSolitonMetrics(peerID string) {
    state := solitonState[peerID]
    
    // Convert IST Eigenvalues and Reflection into a Synara-readable "Flame Score"
    // Flame Score = (1.0 - Reflection) * (Energy / 100)
    flameScore := (1.0 - state.Reflection) * (state.Energy / 100.0)
    
    // Broadcast to Synara Core via Local Socket or Shared Memory
    n.pushToSynara(peerID, flameScore, state.PhaseShift)
}
