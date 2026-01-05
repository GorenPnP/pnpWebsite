#! /bin/bash

BASEPATH_CONTAINER="/var/www"
BASEPATH_HOST="/home/debian/pnpWebsite"
DATE="$(date +%y-%m-%d)"

# move to base path on actual machine
cd $BASEPATH_HOST
mkdir -p ./backups/$DATE/media

docker build --tag 'do_backup' -f ./ppServer/Dockerfile.backup ./ppServer


# stop routing to ensure consistent backup data
docker container stop pnp-webserver

# do db backup
docker run \
    --name do_backup \
    --env-file ./.env.prod \
    --network=pnpwebsite_goren \
    do_backup
docker cp do_backup:$BASEPATH_CONTAINER/backups/. ./backups/$DATE/
docker rm do_backup

# backup media
docker cp pnp-web:$BASEPATH_CONTAINER/media/.  ./backups/$DATE/media/

# re-enable routing, rest can be done in parallel
docker container start pnp-webserver


# compress backup
cd ./backups
tar -czf $DATE.tar.gz $DATE/

# remove all files (type f) modified longer than 30 days ago under ./backups
rm -rf ./$DATE
find . -type f -mtime +30 -delete

# copy backup over to google  cloud storage bucket
gcloud storage cp $BASEPATH_HOST/backups/$DATE.tar.gz gs://backup-goren-pnp.appspot.com/backups
