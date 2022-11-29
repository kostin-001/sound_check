import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sound_check.settings')

app = Celery('sound_check')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
