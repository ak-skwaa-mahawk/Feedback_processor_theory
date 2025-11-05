# synara_autonomy.py
import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
QUEUE_DIR = Path("./queue")
SYNC_URL = "https://api.github.com/repos/ak-skwaa-mahawk/Feedback_processor_theory/contents/queue"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # store your token in env vars
TASK_INTERVAL = 300  # 5 minutes

# Ensure queue directory exists
QUEUE_DIR.mkdir(exist_ok=True)

# --- TASKS ---
def run_local_tasks():
    """
    Define tasks Synara should perform offline.
    Example: process files, update local logs, compute resonance metrics.
    """
    timestamp = datetime.utcnow().isoformat()
    task_result = {
        "time": timestamp,
        "message": "Task completed successfully",
        "data": {}  # add relevant data here
    }

    # Save task result to queue
    task_file = QUEUE_DIR / f"task_{int(time.time())}.json"
    with open(task_file, "w") as f:
        json.dump(task_result, f)
    print(f"[{timestamp}] Queued task: {task_file.name}")

# --- SYNC FUNCTION ---
def sync_queue():
    """
    Attempt to push queued tasks to GitHub when network is available.
    """
    files = list(QUEUE_DIR.glob("*.json"))
    if not files:
        return

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for file in files:
        with open(file, "r") as f:
            content = f.read()

        # GitHub requires base64-encoded content
        import base64
        b64_content = base64.b64encode(content.encode()).decode()

        # Prepare payload
        payload = {
            "message": f"Autonomy sync: {file.name}",
            "content": b64_content
        }

        try:
            response = requests.put(f"{SYNC_URL}/{file.name}", headers=headers, json=payload)
            if response.status_code in [200, 201]:
                print(f"[SYNC] Successfully uploaded {file.name}")
                file.unlink()  # remove local copy after successful sync
            else:
                print(f"[SYNC] Failed to upload {file.name}: {response.status_code}")
        except Exception as e:
            print(f"[SYNC] Exception during sync: {e}")

# --- MAIN LOOP ---
def main():
    print("[Synara Autonomy] Starting loop...")
    while True:
        try:
            run_local_tasks()
            sync_queue()
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(TASK_INTERVAL)

if __name__ == "__main__":
    main()

