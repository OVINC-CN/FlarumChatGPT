#! /bin/sh

python manage.py migrate --noinput
nohup celery worker -c 1 -l INFO -f /usr/src/app/celery-logs/worker.log >/dev/null 2>&1 &
nohup celery beat -l INFO -f /usr/src/app/celery-logs/beat.log >/dev/null 2>&1 &
tail -f /dev/null
