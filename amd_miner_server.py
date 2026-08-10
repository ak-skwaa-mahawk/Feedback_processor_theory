# amd_miner_server.py
import socket
import json

HOST = "0.0.0.0"
PORT = 5005

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("AMD Miner Listening for Pi Nodes...")
    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(4096)
            if data:
                payload = json.loads(data)
                R = payload["R"]
                reward = int(R * 100) if R > 0.997 else 0
                print(f"Mined {reward} Ψ | From {payload['node']}")