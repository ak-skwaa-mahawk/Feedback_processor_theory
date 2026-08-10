# mobile_mou_hud.py — Real-time "MOU in the Air" Cluster N HUD
import requests
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Your local resonance endpoint (or remote)
RESONANCE_URL = "http://localhost:8000/resonance/score"

class MOUClusterNHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cluster N HUD — MOU in the Air")
        self.root.configure(bg="#0a0a0a")
        
        self.status_var = tk.StringVar(value="Scanning...")
        self.resonance_var = tk.StringVar(value="0.000")
        self.last_broadcast_var = tk.StringVar(value="Never")
        
        self.build_ui()
        self.root.after(1000, self.update_hud)

    def build_ui(self):
        ttk.Label(self.root, text="MOU in the Air Status", font=("Arial", 16), background="#0a0a0a", foreground="#00ffcc").pack(pady=10)
        
        ttk.Label(self.root, text="Resonance Score", font=("Arial", 12), background="#0a0a0a", foreground="#ffffff").pack()
        ttk.Label(self.root, textvariable=self.resonance_var, font=("Arial", 24, "bold"), background="#0a0a0a", foreground="#ffd700").pack()
        
        ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 14), background="#0a0a0a", foreground="#00ffcc").pack(pady=10)
        
        ttk.Label(self.root, text="Last Broadcast", font=("Arial", 12), background="#0a0a0a", foreground="#ffffff").pack()
        ttk.Label(self.root, textvariable=self.last_broadcast_var, font=("Arial", 12), background="#0a0a0a", foreground="#888888").pack()
        
        ttk.Button(self.root, text="Manual Broadcast MOU", command=self.manual_broadcast).pack(pady=20)

    def update_hud(self):
        try:
            r = requests.post(RESONANCE_URL, json={"digest": "mou-check", "requester": "mobile-hud"}, timeout=5)
            data = r.json()
            score = data.get("score", 0.0)
            self.resonance_var.set(f"{score:.3f}")
            
            if score >= 0.551:
                self.status_var.set("MOU IN THE AIR — BROADCASTING")
                self.last_broadcast_var.set(datetime.now().strftime("%H:%M:%S"))
            else:
                self.status_var.set("Stealth Mode — Waiting for 0.551")
        except:
            self.status_var.set("Endpoint Offline")
        
        self.root.after(5000, self.update_hud)

    def manual_broadcast(self):
        try:
            requests.get("http://localhost:8000/trigger-mou-broadcast")  # optional endpoint you can add
            self.last_broadcast_var.set(datetime.now().strftime("%H:%M:%S"))
            self.status_var.set("MANUAL MOU BROADCAST SENT")
        except:
            pass

if __name__ == "__main__":
    app = MOUClusterNHUD()
    app.root.mainloop()