import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

Celery_app = Celery('proj')
Celery_app.config_from_object('django.conf:settings', namespace='CELERY')
Celery_app.autodiscover_tasks()