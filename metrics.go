// metrics.go — v2.1 Corrected Telemetry (Unix Epoch + Gradient Mass)
package main

import (
    "strconv"
    "time"
)

func parseWGMetrics(fields []string) (float64, bool) {
    // fields[4] is unix timestamp in seconds (real wg dump)
    ts, _ := strconv.ParseInt(fields[4], 10, 64)
    if ts == 0 {
        return 0.0, false // Never handshaked = Zero Mass
    }

    handshake := time.Unix(ts, 0)
    staleDuration := time.Since(handshake)

    // Gradient Mass: 1.0 (fresh) → 0.0 (3 mins stale)
    mass := 1.0 - (staleDuration.Seconds() / 180.0)
    if mass < 0 {
        mass = 0
    }

    return mass, true
}