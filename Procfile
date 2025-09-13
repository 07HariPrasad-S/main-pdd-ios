web: gunicorn config.wsgi
worker: celery -A celery_config worker --loglevel=info --pool=solo
