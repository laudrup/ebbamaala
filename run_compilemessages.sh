#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    source env/bin/activate
fi

export DJANGO_SECRET_KEY=decafbad
export DJANGO_DS_API_KEY=decafbad
python manage.py compilemessages
