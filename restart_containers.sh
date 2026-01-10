#! /bin/bash

git pull

docker compose -f docker-compose.vis.yml pull
docker compose -p visual -f docker-compose.vis.yml up -d --build --remove-orphans

docker compose -f docker-compose.prod.yml pull
docker compose -p pnpwebsite -f docker-compose.prod.yml up -d --build --remove-orphans

docker system prune -a
