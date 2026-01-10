# Server of the Goren PnP

- [git-repo](https://github.com/GorenPnP/pnpWebsite) on Github
- domain purchased from [GoDaddy](https://dcc.godaddy.com/control/goren-pnp.de/dns?plid=1&plid=1&sc_code=1)
- nameserver from [Cloudflare](https://dash.cloudflare.com/354217e3b0c6583d323ac8fe5cdde94a/goren-pnp.de)
- SSL-Cert from LetsEncrypt for goren-pnp.de on machine, not dockerized
- hosted on [OVH Cloud](https://www.ovh.com/manager/dedicated/#/vps/vps-fbeb6d68.vps.ovh.net/dashboard)
- [Sentry-monitoring](https://sentry.io/organizations/i-org/issues/?project=6128752)


## Dev setup **with** Docker

### create
- install Docker
- install node/npm
- `cd ppServer && npm i`

### use
- `docker compose -p visual -f docker-compose.vis.yml up -d --build --remove-orphans`
- `docker compose -p pnpwebsite -f docker-compose.dev.yml up -d --build --remove-orphans`
- `./ppServer/node_modules/.bin/sass ppServer/backend --watch`
- `./ppServer/node_modules/.bin/tsc --watch ppServer`


## Dev setup **without** Docker

### create

**Virtual python env**
- create `python3 -m venv ./venv`
- enter `./venv/Scripts/activate`
- leave with `deactivate`

**convert static resources**
- install node/npm
- `cd ppServer && npm i`

### use
- `./venv/Scripts/activate`
- `py ppServer/backend/manage.py runserver 0.0.0.0:80`
- `./ppServer/node_modules/.bin/sass ppServer/backend --watch`
- `./ppServer/node_modules/.bin/tsc --watch ppServer`
- if accessing python, use `py <params>` (if pip is messed up, you can use `py -m pip <params>` to specify the python version of pip, which is the same as of `py`.)


## Setup prod server (potentially incomplete)

### get files
- secure .env files of old server since they are not in version control!
- install docker
- clone repo to /home/debian `cd && git@github.com:GorenPnP/pnpWebsite.git`
- `cd pnpWebsite`
- add previously saved .env files
- restore db & media (see below)

### add Loki-Logging of all docker containers

- run `docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions`
- add option to docker deamon (/etc/docker/daemon.json) on the host machine:
  ```json
  {
    "log-driver": "loki",
    "log-opts": {
      "loki-url": "http://loki:3100/loki/api/v1/push",
      "loki-batch-size": "400"
    }
  }
  ```
- restart docker systemprocess `sudo systemctl restart docker`
- (restart all containers `docker compose ... up --force-recreate`) <- should be currently down, so skip this step

### fail2ban
protect against ssh bruteforce attacks with [fail2ban](https://wiki.ubuntuusers.de/fail2ban/#Status-der-Jails)
- `sudo apt install fail2ban`
- configure for sshd [see this](https://www.golinuxcloud.com/fail2ban-ssh)

- see jail status: `sudo fail2ban-client status sshd`

### init backup
- add cronjob on prod server:
    - `crontab -e`
    - add `0 2 * * * cd ~ && ./pnpWebsite/scripts/backup_db_and_media`

- Authenticate for backup at Google Cloud Storage on prod server
  - download & install gcloud. Docs: https://cloud.google.com/sdk/docs/install?hl=de#deb
  - run `gcloud init` -> auth with own google account


### DNS & ssl
- buy domain, setup DNS on nameserver, e.g. Cloudflare
- Setup ssl-certs with certbot
    - install snap for certbot
        - `sudo apt update && sudo apt install snapd`
        - `sudo snap install core; sudo snap refresh core`
    - install certbot with cloudflare-extension
        - `sudo snap install --classic certbot`
        - `sudo ln -s /snap/bin/certbot /usr/bin/certbot`
        - `sudo snap set certbot trust-plugin-with-root=ok`
        - `sudo snap install certbot-dns-cloudflare`
- issue certs: `sudo certbot certonly --email "v.steinbr@gmail.com" --agree-tos --dns-cloudflare --dns-cloudflare-credentials /root/.secrets/cloudflare.ini -d goren-pnp.de -d www.goren-pnp.de --dry-run`
- (add cronjob for `certbot renew`) -> was already configured for me in /etc/cron.d/certbot

### run
`./restart_containers.sh`


## Restore db & media from backup (local?)

- download (latest) backup from [Google Cloud](https://console.cloud.google.com/storage/browser/backup-goren-pnp.appspot.com/backups?hl=de&project=backup-goren-pnp&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&prefix=&forceOnObjectsSortingFiltering=false)
- unpack (note: backup is a *.tar.gz, sometimes the file-ending is chopped off)
- copy *.psql.bin file into /ppServer/backups
- **If** migrations are the same for current db & backup, run `py manage.py dbrestore` to use the latest or `py manage.py dbrestore -i *.psql` for a specific one.
- **Else** try this:
  - clear the db first: run `py manage.py dbshell` and paste
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
  - exit shell
  - run `py manage.py migrate`
  - `pg_restore  -U admin -d goren_db -1 .\backups\*.psql.bin` (will prompt for password)

### Restore media
- download (latest) backup from [Google Cloud](https://console.cloud.google.com/storage/browser/backup-goren-pnp.appspot.com/backups?hl=de&project=backup-goren-pnp&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&prefix=&forceOnObjectsSortingFiltering=false)
- unpack
- replace /ppServer/backend/media/ folder with media/ folder of backup


## OVH
- update os: [Guide](https://docs.ovh.com/de/public-cloud/upgrade-os/)

### rescue mode on OVH
- reboot into rescue mode via OVH-web-dashboard
- wait for email with credentials
- ssh onto rescue-machine
- `mount /dev/sdb1 /mnt`
- `chroot /mnt /bin/bash`
- fix issue (logs are at `cd /var/logs/`), see [here](https://askubuntu.com/questions/311558/ssh-permission-denied-publickey) for ssh permission denied
- reboot normally via OVH-web-dashboard


## update all containers, including db version on prod

### update postgres version in local/dev

- get latest backup from prod server `$prod> ./scripts/backup_db_and_media.sh` -> download from google cloud
- check if django lib needs update to connect to the new postgres version
- change docker-imageversion in docker-compose.(prod | dev).yml -> services -> db -> image
- rm postgres volume `docker volume remove pnpwebsite_postgres_data`
- start db again `docker compose -p pnpwebsite -f docker-compose.dev.yml up -d --build db`
- make sure `pg_restore` is available (install with `apt install postgresql`)
- apply backup to new db volume `pg_restore -U admin -d goren_db -1 ppServer\backups\*.psql.bin`
- enter db password when prompted
- restart everything `docker compose -p pnpwebsite -f docker-compose.dev.yml up -d --build --remove-orphans`
- commit changes in docker-composes

### on prod

**create db backup and copy container -> prod-server**
- `docker exec pnp-web python manage.py dbbackup`
- `docker cp pnp-web:/home/ppServer/web/backups/. ./postgresbackup/`

**rm all containers to start fresh**
- stop all containers `docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.vis.yml down`
- rm all containers & images `docker container prune` `docker image prune -a`

**rm postgres volume**
- `docker volume ls`
- `docker volume remove pnpwebsite_postgres_data`
- `docker volume ls`
- remove other volumes well, if the container's active user changed and the new one will not have the correct permissions

**restore postgres data**
- `git pull` updates in docker-composes
- change port settings for the db-service. Replace `expose: -5432` to `ports: -5432:5432` in docker-compose.prod.yml 
- start db again `docker compose -p pnpwebsite -f docker-compose.prod.yml up -d db`
- make sure `pg_restore` is available (install with `apt install postgresql`)
- apply backup `pg_restore -U admin -d goren_db -1 postgresbackup/*.psql.bin`
- enter db password when prompted
- change port settings back. Replace `ports: -5432:5432` to `expose: -5432` in docker-compose.prod.yml 
- `rm -rf ./postgresbackup`

**update all (other) containers**
- restart everything `./restart_containers.sh`


## useful commands

### Docker
- see running containers: `docker ps`
- logs: `docker logs <containername>`
- run command in container: `docker exec <containername> <command>`
- run interactive (bash-)shell: `docker exec -it <containername> /bin/bash`

### Django
- See all available backups to restore from: `py manage.py listbackups`
- test if ready for Production, including security `python manage.py check --deploy`

### unpack tar.gz
`tar -xvzf *.tar.gz`

### login as someone else
`sudo -u user2 bash`

### generate self-signed certs (for local testing)
* https://tecadmin.net/step-by-step-guide-to-creating-self-signed-ssl-certificates/
