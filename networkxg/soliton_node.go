// networkxg/soliton_node.go — v2.2 IST-Mapped Node Model
type SolitonState struct {
    PeerID      string
    EigenValue  float64 // stable baseline identity (κⱼ)
    Energy      float64 // dynamic momentum
    Reflection  float64 // packet loss / instability proxy
    PhaseShift  float64 // latency drift after interaction
}

// IST → LDPC Hybrid Propagation (reflectionless + phase-shift rule)
func propagateInfluence(a, b *SolitonState) {
    // Phase shift from interaction (k1 - k2)/(k1 + k2) inspired
    delta := (a.EigenValue - b.EigenValue) / (a.EigenValue + b.EigenValue)
    b.PhaseShift += delta * 0.1

    // Reflection = instability (if > 0.2 → degradation)
    if b.Reflection > 0.2 {
        b.Energy *= 0.85
    }

    // Reflectionless reinforcement from stable peers
    if a.Reflection < 0.05 {
        b.Energy += 2.0
    }

    // Clamp to physical bounds
    if b.Energy > 100 {
        b.Energy = 100
    }
    if b.Energy < 0 {
        b.Energy = 0
    }
}