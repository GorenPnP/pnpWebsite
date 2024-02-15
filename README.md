# Server of the Goren PnP

`cd ppServer && ./venv/Scripts/activate && py .\manage.py runserver 0.0.0.0:80`

## Virtual Env
- create `python3 -m venv ./venv`
- enter `./venv/Scripts/activate`
- if accessing python, use `py <params>` (if pip is messed up, you can use `py -m pip <params>` to specify the python version of pip, which is the same as of `py`.)
- leave `deactivate`


## DNS things & other integrations
Domain purchased from [GoDaddy](https://dcc.godaddy.com/control/goren-pnp.de/dns?plid=1&plid=1&sc_code=1)

Nameserver from [Cloudflare](https://dash.cloudflare.com/354217e3b0c6583d323ac8fe5cdde94a/goren-pnp.de)

SSL-Cert from LetsEncrypt for goren-pnp.de (auto-renew because of nginx-proxy-letsencrypt, see docker-compose.prod.yml)

Hosted on [OVH Cloud](https://www.ovh.com/manager/dedicated/#/vps/vps-fbeb6d68.vps.ovh.net/dashboard)

[Sentry-monitoring](https://sentry.io/organizations/i-org/issues/?project=6128752)

## Dependencies for Django Backend (outdated, should update to Django 4)

Update via `pip freeze > .\requirements.txt`

```python
Django==4.*							# need django for django. Makes sense, right?

#Twisted==20.3.0                 # set specific version to use in uvicorn (asgi-server)
#uvicorn[standard]               # asgi server, need async for websockets in chat (does not exist in alpine version of docker-image)
#gunicorn>=20.0.4				# prod env for django

Twisted[tls,http2]==21.*        # needed for HTTP/2 support of daphne
daphne==3.*                     # prod env for (sync django &) async django channels (via ws)

Pillow>=8								# image library
psycopg2-binary>=2.8.6					# for postgresql usage
django-dbbackup==3.*        # db + media backup utility

channels==3.*

six==1.* # generate token for email confirmation on signup

```

## sass (locally for development)
`npm i`
`.\node_modules\.bin\sass . --watch`

## Docker
### inspect container
* logs: `docker logs <containername>`
* run command in container: `docker exec <containername> <command>`

    run interactive (bash-)shell: `docker exec -it <containername> /bin/bash`

# unpack tar.gz
`tar -xvzf *.tar.gz`

## Backup db & media via cronjob
add cronjob on serverhost: `sudo crontab -e`
insert `0 2 * * * cd ~ && ./pnpWebsite/scripts/backup_db_and_media`

### Authenticate for backup at Google Cloud Storage
https://cloud.google.com/sdk/docs/install?hl=de#deb
* download & install gcloud
* `gcloud init` & auth with own google account

## Restore db
**Info**: See all available backups to restore from: `py manage.py listbackups`

**Note**: migrations & db-backup have to be using the same format. So use git history if necessary. Ideally the newest versions should work together. 

1. download (latest) backup from [Google Cloud](https://console.cloud.google.com/storage/browser/backup-goren-pnp.appspot.com/backups?hl=de&project=backup-goren-pnp&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&prefix=&forceOnObjectsSortingFiltering=false)
2. unpack (note: backup is a .tar.gz, sometimes the file-ending is chopped off)
3. copy *.psql file into /ppServer/backups
4. run `py manage.py dbrestore` to use the latest or `py manage.py dbrestore -i *.psql` for a specific one

    * if that doesn't work,try this:
        1. clear the db first: run `py manage.py dbshell` and paste
            ```sql
            DO $$ DECLARE
                r RECORD;
            BEGIN
                -- if the schema you operate on is not "current", you will want to
                -- replace current_schema() in query with 'schematodeletetablesfrom'
                -- *and* update the generate 'DROP...' accordingly.
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
            ```
        2. exit shell
        3. run `py manage.py migrate`
        4. try `py manage.py dbrestore` again OR `pg_restore  -U admin -d goren_db -1 .\backups\*.psql.bin` (will prompt for password)

## Restore media
1. download (latest) backup from [Google Cloud](https://console.cloud.google.com/storage/browser/backup-goren-pnp.appspot.com/backups?hl=de&project=backup-goren-pnp&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&prefix=&forceOnObjectsSortingFiltering=false)
1. unpack
1. replace /ppServer/media/ folder with media/ folder of backup

## larp.goren-pnp.de, a wordpress site
* is self-hosted in a docker container
* backups to GoogleDrive
* Cloudflare-setting for /wp-admin: need to have cookie with name "wp" (blocking bots from guessing wp-credentials because they won't be able to access the site without the cookie)

## Run locally
1. spin up db-container `docker-compose start db` (see docker-compose.yml -> db-service)
2. run `py manage.py runserver`

    if that didn't work, you have to add /ppServer/.env.dev and /ppServer/.env.dev.db variables to /ppServer/ppServer/settings.py
3. [open in browser](http://localhost:8000)

## Run in prod
`docker-compose -f docker-compose.prod.yml up --build --remove-orphans -d`

## Setup prod server (incomplete)
1. secure .env files of old server since they are not in version control!
1. install docker
1. clone [git-repo](https://github.com/GorenPnP/pnpWebsite) to /home/debian
1. add previously saved .env files
1. protect against ssh bruteforce attacks with [fail2ban](https://wiki.ubuntuusers.de/fail2ban/#Status-der-Jails) `sudo apt install fail2ban` + configure for sshd [see this](https://www.golinuxcloud.com/fail2ban-ssh), see jail status: `sudo fail2ban-client status sshd`
1. `sudo pip3 install gsutil && sudo gsutil config` (on host) for google cloud connection & auth
1. add cronjob for backups `sudo crontab -e`
1. restore db & media
1. run in prod
1. fiddle with DNS if different IP
1. Setup ssl-certs with certbot
    1. install snap for certbot
        * `sudo apt update && sudo apt install snapd`
        * `sudo snap install core; sudo snap refresh core`
    1. install certbot with cloudflare-extension
        * `sudo snap install --classic certbot`
        * `sudo ln -s /snap/bin/certbot /usr/bin/certbot`
        * `sudo snap set certbot trust-plugin-with-root=ok`
        * `sudo snap install certbot-dns-cloudflare`
1. issue certs: `sudo certbot certonly --email "v.steinbr@gmail.com" --agree-tos --dns-cloudflare --dns-cloudflare-credentials /root/.secrets/cloudflare.ini -d goren-pnp.de -d www.goren-pnp.de --dry-run`
1. (add cronjob for `certbot renew`) -> was already configured for me in /etc/cron.d/certbot

## update os on OVH
[Guide](https://docs.ovh.com/de/public-cloud/upgrade-os/)

## rescue mode on OVH
* reboot into rescue mode via OVH-web-dashboard
* wait for email with credentials
* ssh onto rescue-machine
* `mount /dev/sdb1 /mnt`
* `chroot /mnt /bin/bash`
* fix issue (logs are at `cd /var/logs/`), see [here](https://askubuntu.com/questions/311558/ssh-permission-denied-publickey) for ssh permission denied
* reboot normally via OVH-web-dashboard

## login as someone else
`sudo -u user2 bash`

# Update postgres version

1. check if django libs needs updates to connect to the new version
1. save backup in `.\ppServer\backups\`!
1. make sure `pg_restore` is available (install with `apt install postgresql`)
1. stop db (and everything else) `docker-compose -f .\docker-compose.prod.yml down`
1. remove db-volume (all data will be lost) `docker volume rm pnpwebsite_postgres_data`

## local in dev
1. change docker-imageversion manually in docker-compose.prod.yml -> services -> db -> image
2. start db again `docker-compose -f docker-compose.prod.yml up -d db`
3. apply backup to new db volume `pg_restore -U admin -d goren_db -1 ppServer\backups\*.psql.bin`
4. enter db password when prompted
5. restart everything `docker-compose -f docker-compose.prod.yml up -d`

## prod-server
1. `git pull` changes in `docker-compose.prod.yml`
2. change port settings for the db-service. Replace `expose: -5432` to `ports: -5432:5430` in docker-compose.prod.yml 
3. start db again `docker-compose -f docker-compose.prod.yml up -d db`
4. apply backup `pg_restore -U admin -d goren_db -1 backups/*.psql.bin -p 5430 -h 0.0.0.0`
5. enter db password when prompted
6. change port settings back. Replace `ports: -5432:5430` to `expose: -5432` in docker-compose.prod.yml 
7. restart everything `docker-compose -f docker-compose.prod.yml up -d`

## generate self-signed certs (for local testing)
* https://tecadmin.net/step-by-step-guide-to-creating-self-signed-ssl-certificates/