#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py flush --no-input
# python manage.py migrate

python manage.py collectstatic --noinput && \

npm update npm && npm i && \
./node_modules/sass/sass.js ./static --update --no-source-map

exec "$@"
