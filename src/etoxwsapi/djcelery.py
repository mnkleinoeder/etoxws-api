import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etoxwsapi.settings')

jobmgr = Celery('etoxwsapi')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
jobmgr.config_from_object('django.conf:settings')
jobmgr.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@jobmgr.task(bind=True)
def debug_task(self):
    #print('Request: {0!r}'.format(self.request))
    print "in celery"