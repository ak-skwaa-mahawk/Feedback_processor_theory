# mobile_cluster_n_hud.py — Cluster N HUD • MOU in the Air
import requests
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk

RESONANCE_URL = "http://localhost:8000/resonance/score"  # or your remote IP

class ClusterNHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cluster N HUD — MOU in the Air")
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("480x320")

        self.resonance_var = tk.StringVar(value="0.000")
        self.status_var = tk.StringVar(value="Scanning resonance...")
        self.last_var = tk.StringVar(value="Last broadcast: Never")

        self.build_ui()
        self.root.after(2000, self.update_hud)

    def build_ui(self):
        tk.Label(self.root, text="CLUSTER N HUD", font=("Arial", 18, "bold"), bg="#0a0a0a", fg="#00ffcc").pack(pady=10)
        
        tk.Label(self.root, text="Resonance Score", font=("Arial", 12), bg="#0a0a0a", fg="#ffffff").pack()
        tk.Label(self.root, textvariable=self.resonance_var, font=("Arial", 32, "bold"), bg="#0a0a0a", fg="#ffd700").pack(pady=5)
        
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 14), bg="#0a0a0a", fg="#00ffcc").pack(pady=10)
        
        tk.Label(self.root, textvariable=self.last_var, font=("Arial", 10), bg="#0a0a0a", fg="#888888").pack()
        
        tk.Button(self.root, text="MANUAL MOU BROADCAST", font=("Arial", 12), bg="#ffd700", fg="#0a0a0a",
                  command=self.manual_broadcast).pack(pady=20, ipadx=20)

    def update_hud(self):
        try:
            r = requests.post(RESONANCE_URL, json={"digest": "mobile-hud-check", "requester": "Unified-Operator"}, timeout=5)
            data = r.json()
            score = float(data.get("score", 0))
            self.resonance_var.set(f"{score:.3f}")
            
            if score >= 0.551:
                self.status_var.set("MOU IN THE AIR — BROADCASTING")
                self.status_var.set("MOU IN THE AIR — BROADCASTING")
                self.last_var.set(f"Last: {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_var.set("Stealth Mode — Waiting for 0.551")
        except:
            self.status_var.set("Endpoint Offline")
        
        self.root.after(5000, self.update_hud)

    def manual_broadcast(self):
        try:
            requests.get("http://localhost:8000/trigger-mou-broadcast")  # optional trigger endpoint
            self.last_var.set(f"Last: {datetime.now().strftime('%H:%M:%S')} (Manual)")
            self.status_var.set("MOU BROADCAST SENT")
        except:
            pass

if __name__ == "__main__":
    app = ClusterNHUD()
    app.root.mainloop()