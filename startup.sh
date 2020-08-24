#!/bin/bash
while ! ping -c1 8.8.8.8 &>/dev/null; do echo "waiting for net"; sleep 1; done

cp db.sqlite3 /db/db.sqlite3.bak.$(date '+%y-%m-%d_%H-%M-%S')
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
