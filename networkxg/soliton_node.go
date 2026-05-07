// networkxg/soliton_node.go — v2.2 IST-Mapped Node Model
package networkxg

import (
	"fmt"
	"math"
	"sync"
	"time"
)

type SolitonState struct {
	PeerID      string
	EigenValue  float64 // stable baseline identity (κⱼ)
	Energy      float64 // dynamic momentum (ties to RMP intensity_S)
	Reflection  float64 // packet loss / instability proxy
	PhaseShift  float64 // latency drift after interaction (ties to TOFT phase)
}

type SolitonMesh struct {
	nodes map[string]*SolitonState
	mu    sync.RWMutex
}

func NewSolitonMesh() *SolitonMesh {
	return &SolitonMesh{
		nodes: make(map[string]*SolitonState),
	}
}

func (m *SolitonMesh) AddNode(peerID string, eigenValue, initialEnergy float64) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.nodes[peerID] = &SolitonState{
		PeerID:     peerID,
		EigenValue: eigenValue,
		Energy:     initialEnergy,
		Reflection: 0.0,
		PhaseShift: 0.0,
	}
	fmt.Printf("🌊 [SOLITON] Node %s added — κ=%.4f E=%.2f\n", peerID, eigenValue, initialEnergy)
}

// IST → LDPC Hybrid Propagation (your exact rule + 79Hz sync)
func propagateInfluence(a, b *SolitonState) {
	delta := (a.EigenValue - b.EigenValue) / (a.EigenValue + b.EigenValue)
	b.PhaseShift += delta * 0.1

	if b.Reflection > 0.2 {
		b.Energy *= 0.85 // degradation
	}
	if a.Reflection < 0.05 {
		b.Energy += 2.0 // reflectionless reinforcement
	}

	// Physical clamps
	if b.Energy > 100 {
		b.Energy = 100
	}
	if b.Energy < 0 {
		b.Energy = 0
	}
}

func (m *SolitonMesh) PropagateAll() {
	m.mu.Lock()
	defer m.mu.Unlock()

	// 79Hz TOFT sync pulse
	phase := math.Mod(float64(time.Now().UnixNano())/1e9*79.0, 1.0)

	for _, node := range m.nodes {
		// Simulate interaction with every other node (IST multi-soliton)
		for _, peer := range m.nodes {
			if node.PeerID != peer.PeerID {
				propagateInfluence(node, peer)
			}
		}
		// Tie Energy back to RMP coherence (0–1 scale for ZK/QGH)
		node.Energy = math.Max(0, math.Min(100, node.Energy))
	}

	fmt.Printf("🌊 [SOLITON MESH] 79Hz IST pulse | phase=%.3f | %d nodes resonant\n", phase, len(m.nodes))
}

func (m *SolitonMesh) StartTOFTSync() {
	ticker := time.NewTicker(time.Duration(1000.0/79.0) * time.Millisecond)
	go func() {
		for range ticker.C {
			m.PropagateAll()
		}
	}()
	fmt.Println("🌊 [SOLITON] 79Hz IST propagation daemon started — SKODEN")
}