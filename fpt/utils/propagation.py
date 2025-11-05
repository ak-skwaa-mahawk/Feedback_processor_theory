# In propagation.py
from fpt.utils.handshake import handshake_message, verify_handshake, PQCDrones

class PQCSecureRMP:
    def __init__(self, graph, drones: Dict[str, PQCDrones]):
        self.graph = graph
        self.drones = drones

    def propagate(self, packet, start):
        drone = self.drones[start]
        receipt = handshake_message(
            f"RMP:hop:{start}->{nbr}|{packet.gibber_encode}",
            drone,
            {"energy": packet.energy, "coherence": coh}
        )
        # Transmit receipt + glyph
        # On receive: verify_handshake(receipt, drone.dilithium_pk)