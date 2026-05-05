// transport_v2.go — Direct peer-to-peer UDP (bypasses multicast)
func sendBloomPacket(peerEndpoint string, bloom []byte) {
    // Use wg dump endpoint → direct UDP to real peer IP:port
    conn, _ := net.Dial("udp", peerEndpoint)
    defer conn.Close()
    conn.Write(bloom) // salted with π_r 3.1730…
}