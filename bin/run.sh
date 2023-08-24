#! /bin/sh

python manage.py migrate --noinput
nohup python manage.py celery worker -c 1 -l INFO >/dev/null 2>&1 &
nohup python manage.py celery beat -l INFO >/dev/null 2>&1 &
tail -f /dev/null
