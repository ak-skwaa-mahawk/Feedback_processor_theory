import json, datetime, os

def log_feedback(conversation, output_dir="data/resonance_logs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    log = {
        "timestamp": timestamp,
        "conversation": conversation,
        "length": len(conversation),
        "speakers": list(set([x[0] for x in conversation]))
    }

    file_path = f"{output_dir}/resonance_log_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(log, f, indent=4)

    return file_path