from synara_core.mesh import Mesh
from synara_core.handshake import Handshake

mesh = Mesh()
hand = Handshake(node_id="usb-node-001")

# example subscriber that writes receipts
def writer(glyph):
    hand.create_receipt({"glyph": glyph.to_dict()})

mesh.subscribe(writer)

# main loop (simple)
if __name__ == '__main__':
    # initialize hardware, services, etc.
    while True:
        # wait for incoming events or run scheduled tasks
        import time
        time.sleep(1)