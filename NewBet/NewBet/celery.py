import os
from celery import Celery
from django.conf import settings

# settings for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewBet.settings')
app = Celery('NewBet')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)