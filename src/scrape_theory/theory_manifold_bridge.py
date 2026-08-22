#!/usr/bin/env python3
import glob
import json
import logging
import math
import os
import socket
import struct
import sys
import time
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class TheoryManifoldEmbedder:
    def __init__(self, scrapes_dir="data/scrapes", udp_host="127.0.0.1", udp_port=9999):
        self.scrapes_dir = scrapes_dir
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def extract_text_from_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            if isinstance(data, dict):
                # Handle standard firecrawl payload schemas
                return (
                    data.get("markdown")
                    or data.get("data", {}).get("markdown")
                    or data.get("text")
                    or json.dumps(data)
                )
            return str(data)
        except Exception as e:
            logging.error(f"Error loading {filepath}: {e}")
            return ""

    def text_to_phase_and_lyapunov(self, text_chunk):
        """
        Maps a text chunk into:
          - u (Major Torus Phase): normalized lexical character center-of-mass [0, 2*pi)
          - v (Minor Torus Phase): normalized byte entropy [0, 2*pi)
          - lyapunov: semantic dispersion rate (<0 = coherent/structured, >0 = chaotic)
        """
        if not text_chunk or len(text_chunk.strip()) == 0:
            return 0.0, 0.0, -7.683965

        # 1. Major Phase (u): Character frequency weighted distribution
        char_vals = [ord(c) % 128 for c in text_chunk]
        avg_char = float(np.mean(char_vals))
        u_phase = float((avg_char / 128.0) * 2.0 * math.pi)

        # 2. Minor Phase (v): Shannon entropy of bytes
        byte_counts = {}
        for b in text_chunk.encode("utf-8"):
            byte_counts[b] = byte_counts.get(b, 0) + 1
        
        entropy = 0.0
        total_bytes = len(text_chunk.encode("utf-8"))
        for count in byte_counts.values():
            p = count / total_bytes
            entropy -= p * math.log2(p)

        # Max Shannon entropy for UTF-8 byte stream is ~8.0
        v_phase = float((entropy / 8.0) * 2.0 * math.pi)

        # 3. Dynamic Lyapunov Stability:
        # Standard english prose entropy ~ 4.0 - 5.0 -> negative lambda (stable)
        # Highly repetitive or completely random text pushes toward divergence
        entropy_divergence = abs(entropy - 4.5)
        lyapunov = float(-7.683965 + (entropy_divergence * 2.0))

        return u_phase, v_phase, lyapunov

    def process_and_stream(self, chunk_size=256, delay_sec=0.05):
        json_files = glob.glob(os.path.join(self.scrapes_dir, "*.json"))
        if not json_files:
            logging.warning(f"No scrape files found in {self.scrapes_dir}. Run firecrawl_fusion.py first.")
            return

        logging.info(f"📚 Found {len(json_files)} scraped theory files to project onto manifold.")

        for filepath in json_files:
            logging.info(f"📖 Processing theory file: {filepath}")
            full_text = self.extract_text_from_file(filepath)
            
            # Slice text into sequential semantic windows
            chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]
            
            for idx, chunk in enumerate(chunks):
                u, v, lyap = self.text_to_phase_and_lyapunov(chunk)
                
                # Pack coordinates into 12-byte binary payload: 3 floats (px, py, lyap)
                payload = struct.pack("!3f", u, v, lyap)
                self.sock.sendto(payload, (self.udp_host, self.udp_port))
                
                logging.info(
                    f"🌀 [THEORY -> 4D]: Chunk {idx+1}/{len(chunks)} | "
                    f"Phase=(u:{u:.4f}, v:{v:.4f}) | Lyap={lyap:.4f}"
                )
                time.sleep(delay_sec)

        logging.info("✅ Theory stream to manifold completed.")

if __name__ == "__main__":
    embedder = TheoryManifoldEmbedder()
    embedder.process_and_stream()
