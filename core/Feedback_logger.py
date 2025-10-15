import json, datetime, os, hashlib, math

def log_feedback(conversation, output_dir="data/resonance_logs"):
    """Log conversation with metadata as JSON."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log = {
        "timestamp": timestamp,
        "conversation": conversation,
        "length": len(conversation),
        "speakers": list(set([x[0] for x in conversation])),
        "pi_feedback_constant": math.pi  # π as recursive stability marker
    }
    file_path = f"{output_dir}/resonance_log_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(log, f, indent=4)
    return file_path

def log_metadata(event, data, output_dir="data/resonance_logs"):
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