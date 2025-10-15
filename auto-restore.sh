#!/usr/bin/env bash
# ==============================================================
# Feedback Processor Theory – FlameChain Auto Restore Script (v1)
# Author: John Carroll / Two Mile Solutions LLC
# Purpose: Instantly restore repo from FlameChain backup archives
# ==============================================================

set -euo pipefail

PROJECT_DIR="$HOME/feedback_processor_theory"
BACKUP_ROOT="$PROJECT_DIR/backups"

echo "🔥 [FPT RESTORE] Auto-restore sequence initiated..."
echo "📂 Project directory: $PROJECT_DIR"
echo "📦 Backup directory: $BACKUP_ROOT"

# ---- List backups ----
echo "🔍 Scanning for available backups..."
BACKUPS=($(ls -t "$BACKUP_ROOT"/flamechain_backup_*.zip 2>/dev/null || true))
if [[ ${#BACKUPS[@]} -eq 0 ]]; then
  echo "❌ No backups found in $BACKUP_ROOT."
  exit 1
fi

echo ""
echo "🗂️ Available backups:"
for i in "${!BACKUPS[@]}"; do
  echo "  [$i] $(basename "${BACKUPS[$i]}")"
done

# ---- Select backup ----
read -p "📥 Enter backup number to restore: " choice
if [[ -z "${BACKUPS[$choice]:-}" ]]; then
  echo "❌ Invalid selection."
  exit 1
fi

SELECTED_BACKUP="${BACKUPS[$choice]}"
echo "📦 Selected backup: $(basename "$SELECTED_BACKUP")"

# ---- Confirm overwrite ----
read -p "⚠️ This will overwrite current project state. Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Restore aborted by user."
  exit 1
fi

# ---- Extract backup ----
TMP_DIR="$PROJECT_DIR/.restore_tmp"
echo "📂 Preparing temporary restore directory..."
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "💾 Extracting backup..."
unzip -q "$SELECTED_BACKUP" -d "$TMP_DIR"

# ---- Replace current repo ----
echo "♻️ Restoring files..."
rsync -a --delete "$TMP_DIR"/ "$PROJECT_DIR"/

# ---- Clean up ----
rm -rf "$TMP_DIR"

# ---- Post-restore Git check ----
cd "$PROJECT_DIR"
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo "🧭 Git repository detected — verifying state..."
  git status
else
  echo "⚠️ Warning: .git directory not detected — you may need to re-clone."
fi

# ---- Completion ----
echo "✅ [FPT RESTORE] Repo restored successfully from: $(basename "$SELECTED_BACKUP")"
echo "🧠 Project now stable and ready for operation."