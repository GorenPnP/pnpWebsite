# pull official base image
FROM ubuntu:20.04

# set work directory
WORKDIR /usr/src/ppServer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set Europe/Berlin as timezone. (install tzdata later with apt-get)
RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# dependencies:
# - python3-pip for pip3
# - netcat for nc in entrypoint.sh
# - postgresql-client-12 for dbbackup
# - curl for nodejs for npm
RUN apt-get update && apt-get install -y python3-pip netcat postgresql-client-12 curl tzdata language-pack-de-base

# exec install script for npm v14 by curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
# and install nodejs for npm
RUN apt-get install -y nodejs

# install dependencies
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# install shit via npm
RUN npm update npm && npm i

# run entrypoint.sh
ENTRYPOINT ["/usr/src/ppServer/entrypoint.sh"]