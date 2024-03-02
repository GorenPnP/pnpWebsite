#! /bin/bash

git pull

docker-compose -p visual -f docker-compose.vis.yml up -d --build --remove-orphans
docker-compose -p pnpWebsite -f docker-compose.prod.yml up -d --build --remove-orphans
docker system prune -a
