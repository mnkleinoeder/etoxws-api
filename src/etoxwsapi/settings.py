# Django settings for etoxwsapi project.
import os
import logging
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR	= os.path.abspath(os.path.join(PROJECT_DIR, '..'))

# this var will be set by Apache/WSGI script
# in development it's ignored.
WSGI_SCRIPT_NAME = os.environ.get('WSGI_SCRIPT_NAME', None)

if WSGI_SCRIPT_NAME is not None:
    BASE_URL = WSGI_SCRIPT_NAME
else:
    BASE_URL = '/etoxwsapi'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': os.path.join(PROJECT_DIR, 'local.db'),                      # Or path to database file if using sqlite3.
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    }
#}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "etoxwsapi_dev",
        'USER': "etoxwsapi_dev",
        'PASSWORD': "etoxwsapi_dev"
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')4e(5k!5s$i^r_6&wb!^+&nc$xe(xa@8x&-67l91+h4ma6qz7c'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'etoxwsapi.disable_csrf.DisableCSRF',
)

ROOT_URLCONF = 'etoxwsapi.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
        'etoxwsapi.v2',
        'etoxwsapi.v2.jobs',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# reasonable default for log file
# either in /var/tmp for system account (apache or www-data)
# or in project dir if ran as user
if os.getuid() < 100: # system account
    log_dir = "/var/tmp/etox-%s"%(os.getuid())
else:
    log_dir = os.path.join(ROOT_DIR, 'log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
LOG_FILE = os.path.join(log_dir, "etoxwsapi-v2.log")

LOG_LEVEL  = "ERROR"
LOG_TO_STDOUT = False

# CELERY SETTINGS
BROKER_URL = 'amqp://etoxws:etoxws@localhost:5672/etoxws'
CELERY_RESULT_BACKEND = 'amqp'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

ETOXWS_IMPL_V2_ASYNC = True

# see http://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother
try:
    execfile(os.path.join(PROJECT_DIR, 'settings_local.py'))
except Exception, e:
    print "Failed to import settings_local.py %s"%(e)

for ws in ('ETOXWS_IMPL_V1', 'ETOXWS_IMPL_V2'):
    if ws not in dir():
        raise Exception("Webservice implementation class required: %s"%(ws))

# see http://celery.readthedocs.org/en/latest/configuration.html#celery-always-eager
CELERY_ALWAYS_EAGER = (not ETOXWS_IMPL_V2_ASYNC)

handlers = ['logfile']
if LOG_TO_STDOUT:
    handlers.append('stdout')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
        'formatters': {
                'standard': {
                        'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'console': {
                        'format': '[%(levelname)s] %(filename)s:%(lineno)d: %(message)s'
                },
        },
    'handlers': {
                'logfile': {
                        'level': LOG_LEVEL,
                        'class':'logging.handlers.RotatingFileHandler',
                        'filename': LOG_FILE,
                        'maxBytes': 1024*1024*5, # 5 MB
                        'backupCount': 5,
                        'formatter':'standard',
                },
                'stdout':{
                    'level':'INFO',
                    'class':'logging.StreamHandler',
                    'stream': sys.stdout,
                    'formatter':'console',
                    'level': LOG_LEVEL,
                },
    },
    'loggers': {
        '': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}


