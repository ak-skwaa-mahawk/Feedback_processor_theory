# ble_mesh_node.py
import cv2
import qrcode
from pyzbar import pyzbar
import json

def scan_qr_for_provisioning():
    cap = cv2.VideoCapture(0)
    print("Scan Provisioner QR...")
    while True:
        ret, frame = cap.read()
        qr_codes = pyzbar.decode(frame)
        for qr in qr_codes:
            data = qr.data.decode()
            try:
                prov = json.loads(data)
                print(f"Provisioned! NetKey: {prov['netkey'][:16]}...")
                cap.release()
                return prov
            except:
                pass
        cv2.imshow("Ψ-Scan QR", frame)
        if cv2.waitKey(1) == ord('q'):
            break
    return None

# Run on boot
prov_data = scan_qr_for_provisioning()
if prov_data:
    print("Node Joined Ψ-MESH-2025")