import os, time, secrets
from synara_core.modules.resonance_policy import WhisperReceipt

def setup_module():
    os.environ["WHISPER_SECRET"] = "whisper-secret"

def test_whisper_generate_and_verify():
    subject = "john.iii"
    ts = int(time.time())
    nonce = secrets.token_hex(8)
    sig = WhisperReceipt.generate(subject, ts, nonce)
    assert WhisperReceipt.verify(subject, ts, nonce, sig) is True
    assert WhisperReceipt.verify(subject, ts-9999, nonce, sig) is False  # too old