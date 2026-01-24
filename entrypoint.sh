#!/bin/sh
echo "Applying database migrations..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py loaddata announcement grades groups notificationperiod studentclubs
python manage.py setup_scheduled_tasks
python manage.py qcluster &

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 StronaProjektyKol.wsgi:application