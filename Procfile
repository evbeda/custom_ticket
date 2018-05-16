worker: celery worker -A custom_ticket --loglevel=debug --concurrency=1
release: python manage.py migrate
web: gunicorn custom_ticket.wsgi --log-file -
