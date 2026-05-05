#!/bin/sh

# Only run migrate and collectstatic on first replica
if [ "$REPLICA_ID" = "1" ] || [ -z "$REPLICA_ID" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

if [ "$DJANGO_DEV" = "true" ]; then
  exec python manage.py runserver 0.0.0.0:8011
else
  exec gunicorn medihub.wsgi:application \
    --bind 0.0.0.0:8011 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
fi
