#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE:-http://localhost:8081}

echo "[1] Share (summary) ..."
SHARE=$(curl -s -X POST "$BASE/codex/share" \
  -H 'content-type: application/json' \
  -d '{"path":"flamevault/codex/CODEX-003_XXXX.json","scope":"read_summary","ttl_seconds":600}')
TOKEN=$(echo "$SHARE" | jq -r .token)
echo "TOKEN: $TOKEN"
curl -s "$BASE/codex/verify_token?token=$TOKEN" | jq >/dev/null

echo "[2] Delegate ..."
DEL=$(curl -s -X POST "$BASE/codex/delegate" \
  -H 'content-type: application/json' \
  -d "{\"parent_token\":\"$TOKEN\",\"delegate_to\":\"researcher.alfa\",\"reduced_scope\":\"read_summary\",\"reduced_ttl\":300}")
DELT=$(echo "$DEL" | jq -r .token)
curl -s "$BASE/codex/verify_token?token=$DELT" | jq >/dev/null

echo "[3] Revoke parent, verify fails ..."
curl -s -X POST "$BASE/codex/revoke?token=$TOKEN&reason=cleanup" | jq
set +e
curl -s "$BASE/codex/verify_token?token=$TOKEN" | jq
set -e

echo "[4] Policy inspect ..."
curl -s "$BASE/codex/policy/inspect?collection=unpublished" | jq

echo "[5] Whisper receipt + v2 resonance mint ..."
WHISPER=$(curl -s -X POST "$BASE/codex/whisper/generate?requester=john.iii")
REC=$(echo "$WHISPER" | jq '{timestamp,nonce,signature}')
curl -s -X POST "$BASE/codex/resonance_share/v2" \
  -H 'content-type: application/json' \
  -d "{\"path\":\"flamevault/codex/CODEX-003_XXXX.json\",\"requester\":\"john.iii\",\"collection\":\"unpublished\",\"score\":0.92,\"cited_flames\":[\"0xRESONANCE-MESH-003\"],\"whisper_receipt\":$REC}" | jq