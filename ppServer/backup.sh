#! /bin/bash

cd /var/www
python manage.py dbbackup
# tar -czf media.tar.gz media/
tar -cvf - media/ | gzip -9 > media.tar.gz
mv media.tar.gz ./backups/media.tar.gz
