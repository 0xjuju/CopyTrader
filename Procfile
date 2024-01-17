web: gunicorn tracker_settings.wsgi --log-file -
worker: celery -A tracker worker --beat --scheduler django --loglevel=info

