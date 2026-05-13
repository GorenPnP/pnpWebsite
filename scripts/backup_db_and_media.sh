#! /bin/bash

BASEPATH_CONTAINER="/var/www"
BASEPATH_HOST="/home/debian/pnpWebsite"
DATE="$(date +%y-%m-%d)"
UPLOAD_PATH="https://nextcloud.vanessa-steinbruegge.de/remote.php/dav/files/backup_goren/Shared/Goren/$DATE"
NEXTCLOUD_AUTH=""

# move to base path on actual machine
cd $BASEPATH_HOST
mkdir -p ./backups/$DATE/media
curl -u $NEXTCLOUD_AUTH -X MKCOL $UPLOAD_PATH

docker build --tag 'do_backup' -f ./ppServer/Dockerfile.backup ./ppServer


# stop routing to ensure consistent backup data
docker container stop nginx

# do db backup
docker run \
    --name do_backup \
    --env-file ./.env.prod \
    --volumes-from django \
    --network=pnpwebsite_django_internal \
    do_backup
docker cp do_backup:$BASEPATH_CONTAINER/backups/. ./backups/$DATE/
docker rm do_backup

# re-enable routing, rest can be done in parallel
docker container start nginx


# remove all files (type f) modified longer than 30 days ago under ./backups
find $BASEPATH_HOST/backups -type f -mtime +30 -delete

# upload backup to nextcloud
cd $BASEPATH_HOST/backups/$DATE

# upload db dump
PSQL_FILENAME=$(find ./*.psql.bin -maxdepth 1 -type f -iname *.psql.bin -exec basename {} \;)
curl -u $NEXTCLOUD_AUTH -T $PSQL_FILENAME "$UPLOAD_PATH/$PSQL_FILENAME"

# upload media
#curl -u $NEXTCLOUD_AUTH -T media.tar.gz "$UPLOAD_PATH/media.tar.gz"
