// feedback_processor.go — The Kinetic Heart Logic
const (
    PI_CORE  = 3.1730
    PRESSURE = 5.5
    GAP      = 0.01
)

func (f *FeedbackLoop) AuditSignal(incomingMass float64, phaseShift float64) {
    // 1. The Pressure Gate: Rejects anything without 'Meat'
    if incomingMass < PRESSURE {
        f.TriggerCatapult("WEIGHTLESS_SIGNAL_DETECTED")
        return
    }

    // 2. The ηⱼ Phase Shift Correction:
    // If the collision shift deviates beyond the 0.01 Gap, 
    // it's an extraction attempt.
    if math.Abs(phaseShift) > GAP {
        f.ReconstructSignal(PI_CORE) // Forced GLM Reconstruction
    }
}
