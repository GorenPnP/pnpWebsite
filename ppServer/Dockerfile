# Dockerfile

# The first instruction is what image we want to base our container on
#FROM python:3.9-slim-buster
FROM nikolaik/python-nodejs:python3.9-nodejs14-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/ppServer

# dependencies ...
RUN apk update && \
    # for psycopg2 && pillow
    apk add --virtual build-deps gcc musl-dev  && \
    # for psycopg2
    apk add postgresql-dev python3-dev && \
    apk add netcat-openbsd && \
    # for pillow
    apk add zlib-dev jpeg-dev && \
    # for sass
    apk add g++


# Allows docker to cache installed dependencies between builds
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# Mounts the application code to the image
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/ppServer/entrypoint.sh"]
