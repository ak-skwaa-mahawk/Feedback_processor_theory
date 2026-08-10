#!/bin/bash
# TWO MILE SOLUTIONS LLC - Sovereign Backup Script
# Requires: restic, rclone (configured for your off-site target like S3/B2)
# Place in /opt/sovereign-backup/ and chmod +x backup.sh

set -euo pipefail  # Exit on error, undefined vars, pipe failures

export RESTIC_REPOSITORY="rclone:remote:n8n-backups"
export RESTIC_PASSWORD_FILE="/opt/sovereign-backup/restic_password.txt"
BACKUP_LOG="/var/log/sovereign-backup.log"

# Function: Log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S AKST')] $1" | tee -a "$BACKUP_LOG"
}

# 1. Pre-flight check: Verify restic repo is accessible
log "Pre-flight: Verifying restic repository..."
if ! restic snapshots --last 1 &>/dev/null; then
    log "ERROR: Restic repository unreachable. Aborting backup."
    exit 1
fi

# 2. Backup the database and the key (separate paths)
log "Starting backup: n8n_data + encryption.key"
if restic backup /opt/n8n/n8n_data /opt/n8n/encryption.key --tag "sovereign-shield"; then
    log "Backup successful: $(restic snapshots --last 1 --json | jq -r '.[0].id')"
else
    log "ERROR: Backup failed. Check restic logs."
    exit 1
fi

# 3. Prune old backups (keep last 7 daily, 4 weekly, 6 monthly)
log "Pruning old backups..."
if restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune --tag "sovereign-shield"; then
    log "Prune successful."
else
    log "WARNING: Prune failed. Manual intervention may be required."
fi

# 4. Verify backup integrity (spot-check latest snapshot)
log "Verifying backup integrity..."
if restic check --read-data-subset=5%; then
    log "Integrity check passed."
else
    log "ERROR: Integrity check failed. Backup may be corrupted."
    exit 1
fi

log "Sync Complete: All operations successful."
# Sovereign Shield - Daily 02:00 AKST backup
0 2 * * * /opt/sovereign-backup/backup.sh >> /var/log/sovereign-backup.log 2>&1
#!/bin/bash
# TWO MILE SOLUTIONS LLC - Sovereign Backup Script
# Requires: restic, rclone (configured for your off-site target like S3/B2)

export RESTIC_REPOSITORY="rclone:remote:n8n-backups"
export RESTIC_PASSWORD_FILE="/home/node/restic_password.txt"

# 1. Backup the database and the key (separate paths)
restic backup ./n8n_data ./encryption.key

# 2. Prune old backups (keep last 7 days, 4 weeks)
restic forget --keep-daily 7 --keep-weekly 4 --prune

echo "Sync Complete: $(date)"
