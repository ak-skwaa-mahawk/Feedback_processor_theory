from locust import HttpUser, task, between
import json, time, secrets

class ResonanceUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def share_verify(self):
        # mint via /codex/share
        r = self.client.post("/codex/share", json={
            "path":"codex/CODEX-003.json",
            "scope":"read_summary",
            "ttl_seconds":300
        })
        if r.status_code != 200:
            return
        token = r.json().get("token","")
        self.client.get("/codex/verify_token", params={"token": token})

    @task
    def resonance_share_v2(self):
        # whisper
        req = "load.user"
        wr = self.client.post(f"/codex/whisper/generate?requester={req}")
        if wr.status_code != 200:
            return
        w = wr.json()
        # apply for unpublished
        body = {
            "path":"codex/CODEX-003.json",
            "requester": req,
            "collection":"unpublished",
            "score": 0.92,
            "cited_flames": ["0xRESONANCE-MESH-003"],
            "whisper_receipt": {k:w[k] for k in ("timestamp","nonce","signature")}
        }
        self.client.post("/codex/resonance_share/v2", json=body)