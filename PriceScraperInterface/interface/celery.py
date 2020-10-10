from __future__ import absolute_import, unicode_literals
from django.conf import settings

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PriceScraperInterface.settings')

app = Celery('interface')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks(settings.INSTALLED_APPS)