#!/bin/sh
set -e

# wait for DB
if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  until nc -z $DB_HOST $DB_PORT; do
    sleep 0.5
  done
fi

# wait for redis
if [ -n "$REDIS_HOST" ]; then
  echo "Waiting for redis at $REDIS_HOST:$REDIS_PORT..."
  until nc -z $REDIS_HOST $REDIS_PORT; do
    sleep 0.5
  done
fi

# run migrations
python manage.py migrate --noinput

# collect static
if [ "$DJANGO_COLLECTSTATIC" != "0" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"

