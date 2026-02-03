#!/bin/bash
python3.9 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt
python manage.py collectstatic --noinput --clear