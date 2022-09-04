web: gunicorn project_settings.wsgi --log-file -
worker: celery -A project_settings worker --beat
