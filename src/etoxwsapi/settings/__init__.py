# Django settings for etoxwsapi project.
import os
import sys
import socket

from .secret_key import SECRET_KEY #@UnusedImport @UnresolvedImport
from pprint import pprint

DEBUG = False
TEMPLATE_DEBUG = DEBUG

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.abspath(os.path.join(PROJECT_DIR, '..', '..'))

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

_log_ident = BASE_URL.strip('/')
if not _log_ident:
    _log_ident = 'etoxwsapi'

# reasonable default for log file
# either in /var/tmp for system account (apache or www-data)
# or in project dir if ran as user
#if os.getuid() < 100: # system account
#    log_dir = "/var/tmp/etoxwsapi-%s"%(os.getuid())
#else:
#    log_dir = os.path.join(ROOT_DIR, 'log')
log_dir = "/var/tmp/%s-%s"%(_log_ident, os.getuid())

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
LOG_FILE = os.path.join(log_dir, "etoxwsapi-v2.log")

LOG_LEVEL  = "WARN"
LOG_TO_STDOUT = False

# CELERY SETTINGS
CELERY_RESULT_BACKEND = 'amqp'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_POOL_RESTARTS = True

ETOXWS_IMPL_V2_ASYNC = True

dflt_datefmt = '%d/%b/%Y %H:%M:%S'
dflt_log_prfx = '[%(asctime)s][%(levelname)s]'
dflt_handlers = ['logfile']

try:
    execfile(os.path.join(PROJECT_DIR, 'settings_local.py'))
except Exception, e:
    sys.stderr.write( "Ignoring missing settings_local.py: %s"%(e) )

# see http://celery.readthedocs.org/en/latest/configuration.html#celery-always-eager
CELERY_ALWAYS_EAGER = (not ETOXWS_IMPL_V2_ASYNC)

dflt_logger = {
    'handlers': dflt_handlers,
    'level': LOG_LEVEL,
    'propagate': False,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': dflt_log_prfx + ' %(name)s: %(message)s',
            'datefmt': dflt_datefmt
        },
        'verbose': {
            'format': dflt_log_prfx + ' %(filename)s:%(lineno)d: %(message)s',
            'datefmt': dflt_datefmt
        },
        'pathinfo': {
            'format': dflt_log_prfx + ' %(pathname)s:%(lineno)d: %(message)s',
            'datefmt': dflt_datefmt
        },
    },
    'handlers': {
        'logfile': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1024*1024 * 100, # in MB
            'backupCount': 5,
            'formatter': 'pathinfo'
        },
        'stdout': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'pathinfo',
        },
        'stderr': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'pathinfo',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'pathinfo',
        },
    },
    'loggers': {
        'django':         dflt_logger,
        'django.request': dflt_logger,
        'etoxwsapi': dflt_logger,
    },
    'root': dflt_logger,
}

from kombu import Connection as _conn

with _conn(BROKER_URL) as conn: #@UndefinedVariable
    try:
        simple_queue = conn.SimpleQueue('simple_queue')
    except socket.error, e:
        print "rabbitmq url: ", BROKER_URL #@UndefinedVariable
        print "Warning: could not establish connection to rabbitmq: ",
        if e.errno == 104:
            print "Access problems."
            print "Check that username, password and vhost are correct."
        elif e.errno == 111:
            print "Server process seems down."
            print "Check with 'service rabbitmq-server status'"

#pprint(LOGGING)

