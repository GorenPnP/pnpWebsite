#! /bin/bash

python manage.py dbbackup
tar -czf media.tar.gz media/
mv media.tar.gz ./backups/media.tar.gz
