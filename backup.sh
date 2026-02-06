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
