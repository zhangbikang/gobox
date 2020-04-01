
from celery import Celery
import os
from django.conf import settings
from celery._state import _set_current_app
import sys
import django
from datetime import timedelta
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE","auto_test.settings")
app=Celery("auto_test")
app.config_from_object("django.conf:settings",namespace='CELERY')
app.autodiscover_tasks()
app.conf.update(
    CELERYBEAT_SCHEDULE={
        "get_cpu_mem_job": {
            "task": "get_cpu_mem_job",
            "schedule": crontab(minute=0,hour="*/12"),
            "args":(["2001","1049","2030","12051","3069"],),

        }
    }
)

