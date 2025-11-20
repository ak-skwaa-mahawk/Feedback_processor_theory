import os

INFRA_MODE = os.getenv("INFRA_MODE", "online")

def safe_post(record: dict):
    if INFRA_MODE == "offline":
        # no outbound traffic, just local log
        local_log(f"[OFFLINE] queued: {record}")
        queue_locally(record)
        return

    try:
        post(record)  # your webhook / API call
    except Exception as e:
        local_log(f"[DEGRADED] error posting: {e}")
        queue_locally(record)
def infra_health():
    results = {
        "self": ping("https://your-bare-server.example"),
        "cloudflare": ping("https://your-cf-fronted-endpoint.example"),
    }
    return results