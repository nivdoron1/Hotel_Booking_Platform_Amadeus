import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frobshop.settings')

app = Celery('frobshop')

# Use the settings from Django's settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps (this will discover tasks.py in your apps)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
