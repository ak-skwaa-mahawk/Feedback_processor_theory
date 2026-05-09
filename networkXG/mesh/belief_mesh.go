// networkXG/mesh/belief_mesh.go (updated)

func UpdateBeliefWithTelemetry(a, b *NodeState, fptCoherence float64) {
    delta := a.Confidence - b.Confidence
    if delta > 0 {
        b.Confidence += delta * 0.1 * (fptCoherence / 100.0)
    }
    if b.Reflection > 0.25 {
        b.Confidence *= 0.9
    }
    if b.Confidence > 1.0 {
        b.Confidence = 1.0
    }
}