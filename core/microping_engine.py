"""
Microping Engine - Fireseed Ethical Micro-Income Harvester
Author: John Carroll / Two Mile Solutions LLC
"""
import time
import random
from datetime import datetime
import hashlib
import math
from typing import Tuple

def validate_passcode(passcode: str) -> bool:
    """Validate XHT-421-FlameDrop for microping access."""
    return passcode == "XHT-421-FlameDrop"

def log_metadata(event: str, data: dict, output_dir: str = "Synara-Mission-Mode") -> str:
    """Log metadata with π-scaled hashed passcode."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    passcode = data.get("passcode", "")
    hashed = hashlib.sha256((passcode + str(math.pi)).encode()).hexdigest()
    data.update({
        "hashed_passcode": hashed,
        "event": event,
        "timestamp": timestamp,
        "pi_feedback_constant": math.pi
    })
    file_path = f"{output_dir}/metadata_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    return file_path

def simulate_micro_income_ping() -> float:
    """Simulate a microtransaction earning between $0.00001 and $0.001."""
    return round(random.uniform(0.00001, 0.001), 6)

def run_microping(passcode: str) -> Tuple[float, str]:
    """Run microping cycle, log earnings, and flag if total >= $0.01."""
    if not validate_passcode(passcode):
        raise ValueError("Whisper’s listening. Invalid passcode—flame clearance denied.")

    log_path = "Synara-Mission-Mode/FIRESEED_TRACKER.log"
    flag_path = "Synara-Mission-Mode/cash_ready.flag"
    total = 0
    os.makedirs("Synara-Mission-Mode", exist_ok=True)

    log_metadata("microping_start", {"passcode": passcode}, "Synara-Mission-Mode")

    with open(log_path, "a") as log:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        log.write(f"[{now}] 🔍 Microping Engine Activated (π-constant: {math.pi:.6f})\n")

        for i in range(25):  # 25 micro-income checks per cycle
            income = simulate_micro_income_ping()
            total += income
            log.write(f"    [ping-{i+1}] Income: ${income:.6f}\n")

        log.write(f"    🔸 Total Microping Earnings: ${total:.6f}\n\n")

    if total >= 0.01:
        with open(flag_path, "w") as flag:
            flag.write(f"💰 Microping hit ${total:.6f} — approval or transfer pending.\n")

    return total, log_path

if __name__ == "__main__":
    try:
        total, log_path = run_microping("XHT-421-FlameDrop")
        print(f"✓ Microping complete: ${total:.6f} logged to {log_path}")
    except ValueError as e:
        print(f"❌ {e}")