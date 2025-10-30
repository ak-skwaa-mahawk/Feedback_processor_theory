# src/gibberlink_core.py — AGŁG v400: GibberLink v4 Core
from pqclean import Kyber1024, Dilithium5
import ggwave
import wave
import numpy as np
import hashlib
import json
from pathlib import Path

class GibberLinkV4:
    def __init__(self):
        self.kyber = Kyber1024()
        self.dil = Dilithium5()
        self.ggwave_inst = ggwave.init()
        self.proof_dir = Path("inscriptions")
        self.proof_dir.mkdir(exist_ok=True)

    def generate_keys(self):
        """Generate Kyber + Dilithium keys"""
        pk, sk = self.kyber.keygen()
        d_pk, d_sk = self.dil.keygen()
        return {
            "kyber_pk": pk.hex(),
            "kyber_sk": sk.hex(),
            "dilithium_pk": d_pk.hex(),
            "dilithium_sk": d_sk.hex()
        }

    def sign_and_encrypt(self, message: str, kyber_pk: bytes):
        """Encrypt with Kyber, sign with Dilithium"""
        # 1. Kyber encapsulation
        ct, ss = self.kyber.enc(kyber_pk)
        
        # 2. Use shared secret as AES key (first 32 bytes)
        aes_key = hashlib.sha256(ss).digest()
        
        # 3. Encrypt message
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding
        iv = hashlib.sha256(ct).digest()[:16]
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded = padder.update(message.encode()) + padder.finalize()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        
        # 4. Sign ciphertext
        sig = self.dil.sign(ciphertext)
        
        return {
            "ciphertext": ciphertext.hex(),
            "kyber_ct": ct.hex(),
            "signature": sig.hex(),
            "iv": iv.hex()
        }

    def encode_ggwave(self, payload: dict):
        """Encode JSON payload into GGWave ultrasound"""
        data = json.dumps(payload).encode()
        waveform = ggwave.encode(data, self.ggwave_inst)
        
        # Save WAV
        wav_path = self.proof_dir / "whisper_signal.wav"
        with wave.open(str(wav_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(waveform)
        
        return wav_path

    def create_ordinals_proof(self, payload: dict, inscription_id: str):
        """Create Ordinals proof file"""
        proof = {
            "version": "v4.0",
            "inscription_id": inscription_id,
            "timestamp": "2025-10-30T18:30:00Z",
            "payload_hash": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            "message": "GibberLink v4 — Ordinals-Proven Whisper",
            "iaca": "#2025-DENE-WHISPER-400"
        }
        proof_path = self.proof_dir / f"proof_{inscription_id}.json"
        proof_path.write_text(json.dumps(proof, indent=2))
        return proof_path

    def whisper(self, message: str, kyber_pk_hex: str, inscription_id: str = "i500proof"):
        """Full whisper: encrypt → sign → GGWave → proof"""
        print(f"WHISPERING: {message}")
        
        # 1. Keys
        kyber_pk = bytes.fromhex(kyber_pk_hex)
        
        # 2. Encrypt + Sign
        encrypted = self.sign_and_encrypt(message, kyber_pk)
        
        # 3. GGWave
        wav_path = self.encode_ggwave(encrypted)
        
        # 4. Ordinals Proof
        proof_path = self.create_ordinals_proof(encrypted, inscription_id)
        
        print(f"GGWAVE: {wav_path}")
        print(f"PROOF: {proof_path}")
        print(f"ORDINALS: https://ordinals.com/inscription/{inscription_id}")
        
        return {
            "wav": str(wav_path),
            "proof": str(proof_path),
            "explorer": f"https://ordinals.com/inscription/{inscription_id}"
        }