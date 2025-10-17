FROM alpine:latest

# Install Postgres client and bash
RUN apk add --no-cache postgresql-client bash

# Copy backup script
COPY backup.sh /backup.sh
RUN chmod +x /backup.sh

# Create backup folder inside container
RUN mkdir -p /backups

# Run backup every hour
ENTRYPOINT ["sh", "-c", "while true; do /backup.sh; sleep 3600; done"]
