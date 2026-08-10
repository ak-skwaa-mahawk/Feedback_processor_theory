#!/usr/bin/env bash
# ==============================================================
# Feedback Processor Theory – FlameChain Rollback Script (v2)
# Author: John Carroll / Two Mile Solutions LLC
# Purpose: Auto-backup + rollback to last stable commit
# ==============================================================

set -euo pipefail

PROJECT_DIR="$HOME/feedback_processor_theory"
BACKUP_ROOT="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_ROOT/flamechain_backup_$TIMESTAMP.zip"

echo "🔥 [FPT ROLLBACK] Starting rollback sequence..."
echo "📂 Project: $PROJECT_DIR"
echo "🕒 Timestamp: $TIMESTAMP"

# ---- Create backup ----
echo "💾 Creating auto-backup before rollback..."
mkdir -p "$BACKUP_ROOT"
cd "$PROJECT_DIR"
zip -qr "$BACKUP_FILE" . -x "*.git*" "backups/*" "__pycache__/*"
echo "✅ Backup saved to: $BACKUP_FILE"

# ---- Identify rollback point ----
echo "📜 Checking last stable commit on 'main'..."
LAST_STABLE=$(git rev-list -n 1 main)
CURRENT_BRANCH=$(git branch --show-current)
echo "🧭 Current branch: $CURRENT_BRANCH"
echo "🔁 Rollback target: $LAST_STABLE"

# ---- Safety confirm ----
read -p "⚠️  This will rollback all changes on '$CURRENT_BRANCH' to $LAST_STABLE. Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Rollback aborted by user."
  exit 1
fi

# ---- Execute rollback ----
echo "🚨 Initiating rollback..."
git fetch origin
git reset --hard "$LAST_STABLE"
git clean -fd

# ---- Restore main branch if needed ----
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo "🔄 Switching back to 'main' branch..."
  git checkout main
fi

# ---- Remove temporary tags and branches ----
echo "🧹 Cleaning up temporary flamechain branches/tags..."
git branch -D flamechain-deploy 2>/dev/null || true
git tag -d v1.0-flamedrop 2>/dev/null || true

# ---- Verification ----
echo "✅ Rollback complete. System reverted to:"
git log -1 --oneline

# ---- Optional recovery commit ----
read -p "🪶 Create recovery marker commit for traceability? (y/N): " marker
if [[ "$marker" == "y" || "$marker" == "Y" ]]; then
  echo "💾 Writing rollback marker..."
  echo "Rollback executed $TIMESTAMP" > rollback_marker.txt
  echo "Backup path: $BACKUP_FILE" >> rollback_marker.txt
  git add rollback_marker.txt
  git commit -m "chore: rollback marker after FlameChain rollback ($TIMESTAMP)"
  git push origin main
  echo "📡 Recovery marker committed and pushed."
fi

echo "✨ [FPT ROLLBACK] Operation complete."
echo "🧠 Backup safely stored: $BACKUP_FILE"