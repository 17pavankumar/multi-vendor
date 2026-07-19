# Importing celery_app here means `python manage.py shell` and every
# management command load the Celery app too, so `@shared_task` always
# has an app to bind to — this is Celery's own documented pattern for
# wiring it into a Django project.
from .celery import app as celery_app

__all__ = ("celery_app",)
