# Dockerfile

# The first instruction is what image we want to base our container on
#FROM python:3.9-slim-buster
FROM nikolaik/python-nodejs:python3.9-nodejs14-alpine

WORKDIR /code

# dependencies ...
RUN apk update && \

    # for psycopg2 && pillow
    apk add --virtual build-deps gcc musl-dev  && \

    # for psycopg2
    apk add postgresql-dev && \
    apk add netcat-openbsd && \

    # for pillow
    apk add zlib-dev jpeg-dev && \

    # for sass
    apk add g++


# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


COPY package*.json ./
RUN npm update npm && npm ci --only=production


# Mounts the application code to the image
COPY . /code

# django setup
WORKDIR ppServer

RUN python manage.py migrate
RUN python manage.py collectstatic

# sass setup
RUN ../node_modules/sass/sass.js ./static/ --update


EXPOSE 8000

# runs the production server
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

