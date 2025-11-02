=========================== api/service.py ===========================================

from future import annotations import os from typing import Any, Dict, Optional from fastapi import FastAPI, HTTPException, Request, Response from fastapi.responses import FileResponse, JSONResponse from pydantic import BaseModel

from synara_integration.flame_adapter import FlameAdapter from synara_integration.whisper_bridge import HandshakeGate from synara_integration.identity_sync import append_sacred_log, write_backup, seal_artifacts

--- Rate limiting (SlowAPI + Redis) ---

from slowapi import Limiter, _rate_limit_exceeded_handler  # rate limiting from slowapi.util import get_remote_address from slowapi.errors import RateLimitExceeded from slowapi.middleware import SlowAPIMiddleware

REDIS_URL = os.getenv("WHISPER_REDIS_URL", "redis://localhost:6379/0") RATE_LIMIT = os.getenv("FPT_RATE_LIMIT", "10/minute")  # legacy single-limit (kept) BURST_LIMIT = os.getenv("FPT_BURST_LIMIT", "5/10second")  # e.g., 5 req / 10 seconds SUSTAINED_LIMIT = os.getenv("FPT_SUSTAINED_LIMIT", "100/hour")  # e.g., 100 req / hour GLOBAL_DEFAULTS = [BURST_LIMIT, SUSTAINED_LIMIT]

Prefer per-user key via receipt.key_id; fallback to client IP

async def key_func(request: Request) -> str: try: body = await request.json() rid = body.get("receipt", {}).get("key_id") if rid: return f"kid:{rid}" except Exception: pass return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=key_func, storage_uri=REDIS_URL, default_limits=GLOBAL_DEFAULTS)

Shared limiters for /fpt/analyze so burst + sustained are enforced per key

burst_limit = limiter.shared_limit(BURST_LIMIT, scope="analyze-burst") sustained_limit = limiter.shared_limit(SUSTAINED_LIMIT, scope="analyze-sustained")

app = FastAPI(title="Feedback Processor Theory — Synara Bridge", version="v1") app.state.limiter = limiter

Replace default handler with a telemetry-rich JSON 429

import time from fastapi import Request from fastapi.responses import JSONResponse

@app.exception_handler(RateLimitExceeded) async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded): state = getattr(request, "state", None) lim = getattr(state, "limiter", None) limit_str = RATE_LIMIT remaining = None reset_time = None retry_after = None if lim is not None: try: limit_obj = getattr(lim, "current_limit", None) if limit_obj is not None and getattr(limit_obj, "limit", None) is not None: limit_str = str(limit_obj.limit) remaining = getattr(lim, "remaining", None) reset_time = getattr(lim, "reset_time", None) if reset_time is not None: retry_after = max(0, int(reset_time - time.time())) except Exception: pass headers = { "Retry-After": str(retry_after or 0), "X-RateLimit-Limit": str(limit_str), "X-RateLimit-Remaining": str(remaining if remaining is not None else 0), "X-RateLimit-Reset": str(reset_time or 0), } body = { "status": "error", "detail": "rate_limit_exceeded", "retry_after": retry_after or 0, "rate_limit": str(limit_str), "remaining": remaining if remaining is not None else 0, "reset_time": reset_time or 0, } return JSONResponse(status_code=429, content=body, headers=headers)

Keep SlowAPI middleware active

app.add_middleware(SlowAPIMiddleware)

adapter = FlameAdapter() handshake = HandshakeGate()

class AnalyzeBody(BaseModel): conversation: str receipt: Dict[str, Any] expected_challenge: Optional[str] = None meta: Optional[Dict[str, Any]] = None

@app.get("/health") def health(): return {"ok": True, "service": app.title, "version": app.version}

@app.get("/live") async def live(): """Liveness probe: app process is running and can serve HTTP.""" return {"status": "live", "service": app.title, "version": app.version}

@app.get("/ready") async def ready(): """Readiness probe: verifies Redis availability for rate limiting.""" redis_ok = False try: import redis  # type: ignore r = redis.Redis.from_url(REDIS_URL) redis_ok = bool(r.ping()) except Exception: redis_ok = False if not redis_ok: # still return 503 so load balancers keep probing until ready from fastapi import status return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={ "status": "not_ready", "redis": {"url": REDIS_URL, "reachable": False} }) return {"status": "ready", "redis": {"url": REDIS_URL, "reachable": True}}

@app.get("/limits") async def limits(request: Request): """Debug endpoint showing limiter configuration and computed key.""" try: computed_key = await key_func(request) except Exception: computed_key = f"ip:{get_remote_address(request)}" return { "rate_limit": RATE_LIMIT, "burst_limit": BURST_LIMIT, "sustained_limit": SUSTAINED_LIMIT, "global_defaults": GLOBAL_DEFAULTS, "storage_uri": REDIS_URL, "computed_key": computed_key, }

@app.get("/config") async def config(): """Operational config & Redis reachability (safe to expose).""" # Try Redis ping without crashing the app if unavailable redis_ok = False redis_info = None try: import redis  # type: ignore r = redis.Redis.from_url(REDIS_URL) redis_ok = bool(r.ping()) # keep meta minimal redis_info = {"client_name": str(r.client_info().get("name", "")) if hasattr(r, "client_info") else None} except Exception as e: redis_info = {"error": str(e.class.name)}

return {
    "service": app.title,
    "version": app.version,
    "rate_limits": {
        "burst_limit": BURST_LIMIT,
        "sustained_limit": SUSTAINED_LIMIT,
        "route_cap": RATE_LIMIT,
        "global_defaults": GLOBAL_DEFAULTS,
    },
    "redis": {
        "url": REDIS_URL,
        "reachable": redis_ok,
        "info": redis_info,
    },
}

@app.post("/fpt/analyze") @burst_limit @sustained_limit @limiter.limit(RATE_LIMIT) async def analyze(request: Request, body: AnalyzeBody): ok, reason, ctx = handshake.verify(body.receipt, expected_challenge=body.expected_challenge) if not ok: raise HTTPException(status_code=401, detail=f"handshake_failed:{reason}")

# 1) compute metrics
metrics = adapter.analyze_resonance(body.conversation)

# 2) build sacred entry
entry = {
    "context": ctx,
    "meta": body.meta or {},
    "metrics": metrics,
}

# 3) persist (log + backup)
append_sacred_log(entry)
backup_path = write_backup(entry)

# 4) seal the result
seal = seal_artifacts("fpt_result", {**entry, "backup": str(backup_path)})

# 5) build response with rate-limit headers
headers = {}
state = request.state.limiter  # type: ignore
if hasattr(state, "current_limit"):
    headers = {
        "X-RateLimit-Limit": str(state.current_limit.limit if state.current_limit else RATE_LIMIT),
        "X-RateLimit-Remaining": str(state.remaining),
        "X-RateLimit-Reset": str(state.reset_time),
    }
data = {
    "status": "ok",
    "reason": reason,
    "context": ctx,
    "metrics": metrics,
    "backup": str(backup_path),
    "seal": seal,
}
return JSONResponse(content=data, headers=headers)

@app.get("/fpt/logs/latest") async def logs_latest(): from pathlib import Path from synara_integration.identity_sync import SACRED_LOG if not SACRED_LOG.exists(): raise HTTPException(status_code=404, detail="no_logs") import json data = json.loads(SACRED_LOG.read_text(encoding="utf-8")) if not data: raise HTTPException(status_code=404, detail="empty_logs") return {"latest": data[-1]}

@app.get("/fpt/qr.png") async def last_qr(): from pathlib import Path p = Path("data") pngs = sorted(p.glob("*.sigil.png"), reverse=True) if not pngs: raise HTTPException(status_code=404, detail="no_qr") return FileResponse(str(pngs[0]), media_type="image/png")

Run with: uvicorn api.service:app --host 0.0.0.0 --port 8081 --reload

=========================== deploy/health.yaml ===========================

apiVersion: apps/v1 kind: Deployment metadata: name: fpt-synara-bridge spec: replicas: 1 selector: matchLabels: app: fpt-synara-bridge template: metadata: labels: app: fpt-synara-bridge spec: containers: - name: fpt-synara-bridge image: twomilesolutions/fpt-synara:latest ports: - containerPort: 8081 livenessProbe: httpGet: path: /live port: 8081 initialDelaySeconds: 10 periodSeconds: 20 timeoutSeconds: 3 failureThreshold: 3 successThreshold: 1 readinessProbe: httpGet: path: /ready port: 8081 initialDelaySeconds: 5 periodSeconds: 10 timeoutSeconds: 3 failureThreshold: 3 successThreshold: 1 env: - name: WHISPER_REDIS_URL value: "redis://redis:6379/0" - name: FPT_RATE_LIMIT value: "10/minute" - name: FPT_BURST_LIMIT value: "5/10second" - name: FPT_SUSTAINED_LIMIT value: "100/hour"

=========================== Dockerfile.append ===========================

Append to your Dockerfile bottom for built-in container health monitoring

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 
CMD curl -fs http://localhost:8081/ready || exit 1

=========================== deploy/redis.yaml ===========================

apiVersion: v1 kind: Service metadata: name: redis spec: selector: app: redis ports: - name: redis port: 6379 targetPort: 6379

apiVersion: apps/v1 kind: Deployment metadata: name: redis spec: replicas: 1 selector: matchLabels: app: redis template: metadata: labels: app: redis spec: containers: - name: redis image: redis:7-alpine args: ["--save", "60", "1", "--loglevel", "warning"] ports: - containerPort: 6379 resources: requests: cpu: 100m memory: 128Mi limits: cpu: 500m memory: 512Mi readinessProbe: tcpSocket: port: 6379 initialDelaySeconds: 3 periodSeconds: 5 livenessProbe: tcpSocket: port: 6379 initialDelaySeconds: 10 periodSeconds: 10 volumeMounts: - name: redis-data mountPath: /data volumes: - name: redis-data emptyDir: {}

=========================== deploy/redis-persistent.yaml ===========================

apiVersion: v1 kind: Service metadata: name: redis labels: app: redis spec: ports: - name: redis port: 6379 targetPort: 6379 clusterIP: None  # headless for stable network ID selector: app: redis

apiVersion: apps/v1 kind: StatefulSet metadata: name: redis spec: serviceName: redis replicas: 1 selector: matchLabels: app: redis template: metadata: labels: app: redis spec: containers: - name: redis image: redis:7-alpine args: ["--save", "60", "1", "--loglevel", "warning"] ports: - containerPort: 6379 readinessProbe: tcpSocket: port: 6379 initialDelaySeconds: 3 periodSeconds: 5 livenessProbe: tcpSocket: port: 6379 initialDelaySeconds: 10 periodSeconds: 10 resources: requests: cpu: 100m memory: 128Mi limits: cpu: 500m memory: 512Mi volumeMounts: - name: redis-data mountPath: /data volumeClaimTemplates: - metadata: name: redis-data spec: accessModes: ["ReadWriteOnce"] storageClassName: "standard"  # <— change to your cluster's StorageClass resources: requests: storage: 5Gi

=========================== helm/fpt-synara/Chart.yaml ===========================

apiVersion: v2 name: fpt-synara description: Feedback Processor Theory — Synara Bridge (FastAPI + SlowAPI + Redis limiter) type: application version: 0.1.0 appVersion: "v1"

=========================== helm/fpt-synara/values.yaml ===========================

image: repository: twomilesolutions/fpt-synara tag: latest pullPolicy: IfNotPresent

service: type: ClusterIP port: 8081

redis: url: "redis://redis:6379/0" # override per env

rateLimits: routeCap: "10/minute" burst: "5/10second" sustained: "100/hour"

resources: limits: cpu: 500m memory: 512Mi requests: cpu: 100m memory: 256Mi

replicaCount: 1

readiness: path: /ready initialDelaySeconds: 5 periodSeconds: 10 timeoutSeconds: 3

liveness: path: /live initialDelaySeconds: 10 periodSeconds: 20 timeoutSeconds: 3

ingress: enabled: false className: "" annotations: {} hosts: - host: fpt.local paths: - path: / pathType: Prefix tls: []

=========================== helm/fpt-synara/templates/_helpers.tpl ===========================

{{- define "fpt-synara.fullname" -}} {{- printf "%s-%s" .Release.Name "fpt-synara" | trunc 63 | trimSuffix "-" -}} {{- end -}}

=========================== helm/fpt-synara/templates/deployment.yaml ===========================

apiVersion: apps/v1 kind: Deployment metadata: name: {{ include "fpt-synara.fullname" . }} labels: app.kubernetes.io/name: fpt-synara app.kubernetes.io/instance: {{ .Release.Name }} spec: replicas: {{ .Values.replicaCount }} selector: matchLabels: app.kubernetes.io/name: fpt-synara app.kubernetes.io/instance: {{ .Release.Name }} template: metadata: labels: app.kubernetes.io/name: fpt-synara app.kubernetes.io/instance: {{ .Release.Name }} spec: containers: - name: api image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}" imagePullPolicy: {{ .Values.image.pullPolicy }} ports: - containerPort: {{ .Values.service.port }} env: - name: WHISPER_REDIS_URL value: "{{ .Values.redis.url }}" - name: FPT_RATE_LIMIT value: "{{ .Values.rateLimits.routeCap }}" - name: FPT_BURST_LIMIT value: "{{ .Values.rateLimits.burst }}" - name: FPT_SUSTAINED_LIMIT value: "{{ .Values.rateLimits.sustained }}" readinessProbe: httpGet: path: {{ .Values.readiness.path }} port: {{ .Values.service.port }} initialDelaySeconds: {{ .Values.readiness.initialDelaySeconds }} periodSeconds: {{ .Values.readiness.periodSeconds }} timeoutSeconds: {{ .Values.readiness.timeoutSeconds }} livenessProbe: httpGet: path: {{ .Values.liveness.path }} port: {{ .Values.service.port }} initialDelaySeconds: {{ .Values.liveness.initialDelaySeconds }} periodSeconds: {{ .Values.liveness.periodSeconds }} timeoutSeconds: {{ .Values.liveness.timeoutSeconds }} resources: limits: cpu: {{ .Values.resources.limits.cpu }} memory: {{ .Values.resources.limits.memory }} requests: cpu: {{ .Values.resources.requests.cpu }} memory: {{ .Values.resources.requests.memory }}

=========================== helm/fpt-synara/templates/service.yaml ===========================

apiVersion: v1 kind: Service metadata: name: {{ include "fpt-synara.fullname" . }} labels: app.kubernetes.io/name: fpt-synara app.kubernetes.io/instance: {{ .Release.Name }} spec: type: {{ .Values.service.type }} ports: - port: {{ .Values.service.port }} targetPort: {{ .Values.service.port }} protocol: TCP name: http selector: app.kubernetes.io/name: fpt-synara app.kubernetes.io/instance: {{ .Release.Name }}

=========================== helm/fpt-synara/templates/ingress.yaml ===========================

{{- if .Values.ingress.enabled -}} apiVersion: networking.k8s.io/v1 kind: Ingress metadata: name: {{ include "fpt-synara.fullname" . }} {{- with .Values.ingress.annotations }} annotations: {{- toYaml . | nindent 4 }} {{- end }} spec: {{- if .Values.ingress.className }} ingressClassName: {{ .Values.ingress.className }} {{- end }} rules: {{- range .Values.ingress.hosts }} - host: {{ .host }} http: paths: {{- range .paths }} - path: {{ .path }} pathType: {{ .pathType }} backend: service: name: {{ include "fpt-synara.fullname" $ }} port: number: {{ $.Values.service.port }} {{- end }} {{- end }} {{- if .Values.ingress.tls }} tls: {{- toYaml .Values.ingress.tls | nindent 4 }} {{- end }} {{- end }}

=========================== helm/fpt-synara/templates/NOTES.txt ===========================

Your release {{ .Release.Name }} for fpt-synara is deployed.

Service URL (ClusterIP): kubectl port-forward svc/{{ include "fpt-synara.fullname" . }} 8081:{{ .Values.service.port }} curl -s localhost:8081/health | jq

Rate limits: routeCap={{ .Values.rateLimits.routeCap }} burst={{ .Values.rateLimits.burst }} sustained={{ .Values.rateLimits.sustained }}

Redis URL: {{ .Values.redis.url }}