worker: celery worker -A custom_ticket --loglevel=debug -E
release: python manage.py migrate
web: gunicorn custom_ticket.wsgi --log-file -
