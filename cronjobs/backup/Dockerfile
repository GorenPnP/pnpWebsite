FROM alpine:3.12

# needed to backup postgres-db
RUN apk add --no-cache postgresql-client

# use cronjob to scedule backups of db & media
COPY backup_db_and_media /bin/backup_db_and_media
RUN chmod +x /bin/backup_db_and_media

COPY root /var/spool/cron/crontabs/root

CMD crond -l 2 -f