#!/bin/bash
cp /db/db.sqlite3 /db/db.sqlite3.bak.$(date '+%y-%m-%d_%H-%M-%S')
python manage.py migrate
python manage.py runserver 0.0.0.0:80

