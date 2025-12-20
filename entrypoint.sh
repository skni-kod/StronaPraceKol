#!/bin/sh
echo "Applying database migrations..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 StronaProjektyKol.wsgi:application
