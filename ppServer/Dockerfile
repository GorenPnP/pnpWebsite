# pull official base image
FROM nikolaik/python-nodejs:python3.9-nodejs14-alpine

# set work directory
WORKDIR /usr/src/ppServer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# dependencies ...
RUN apk update && \
    # for psycopg2
    apk add --virtual build-deps gcc musl-dev  && \
    # for psycopg2
    apk add postgresql-dev python3-dev && \
    apk add netcat-openbsd && \
    # for pillow
    apk add zlib-dev jpeg-dev && \
    # for dbbackup
    apk add postgresql && \
    # for channels
    apk add gcc libffi-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/ppServer/entrypoint.sh"]