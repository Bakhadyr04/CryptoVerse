import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cryptoverse.settings')

app = Celery('cryptoverse')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
