# pull official base image
FROM nikolaik/python-nodejs:python3.8-nodejs14-slim

# set work directory
WORKDIR /usr/src/ppServer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# dependencies for nc in entrypoint.sh
RUN apt-get update && apt-get install -y netcat gcc

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