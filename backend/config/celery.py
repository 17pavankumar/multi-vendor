import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("multivendor")

# Reads every CELERY_* setting out of Django's settings.py instead of a
# separate celeryconfig.py — one place to configure the broker URL,
# serialization, timezone, etc.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Finds tasks.py inside every app listed in INSTALLED_APPS automatically
# — a new app's tasks are picked up without editing this file.
app.autodiscover_tasks()
