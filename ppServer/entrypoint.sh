#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python3 manage.py flush --no-input
# python3 manage.py migrate

python3 manage.py collectstatic --noinput && \
 ./node_modules/sass/sass.js ./static --update --no-source-map

exec "$@"
