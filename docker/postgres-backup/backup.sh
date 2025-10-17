#!/bin/bash

# ----------------------------------------
# PostgreSQL Backup Script
# ----------------------------------------
# Performs hourly backup of PostgreSQL database
# Keeps only the last 7 days of backups
# ----------------------------------------

# Ensure backup directory exists
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Load database credentials from environment variables
HOST=${POSTGRES_HOST:-postgres}
USER=${POSTGRES_USER:-postgres}
PASSWORD=${POSTGRES_PASSWORD:-Demon}
DB=${POSTGRES_DB:-srknotesapp-db}

# Generate timestamp for filename
DATE=$(date +'%Y-%m-%d_%H-%M-%S')
FILENAME="$BACKUP_DIR/$DB-backup-$DATE.sql.gz"

# Export password for pg_dump
export PGPASSWORD=$PASSWORD

# Run backup and compress
pg_dump -h $HOST -U $USER $DB | gzip > $FILENAME

# Delete backups older than 7 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -exec rm {} \;

# Log completion
echo "[$(date)] Backup completed: $FILENAME"
