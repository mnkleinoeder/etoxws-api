from .base import *  # @UnusedWildImport

BROKER_URL = 'amqp://etoxwsapi:etoxwsapi@localhost:5672/etoxwsapi'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "etoxwsapi",
        'USER': "etoxwsapi",
        'PASSWORD': "etoxwsapi"
    }
}

from sampleimpl.ws_impl_v1 import WS1
ETOXWS_IMPL_V1 = WS1

from views2 import WS2
ETOXWS_IMPL_V2 = WS2
ETOXWS_IMPL_V2_ASYNC = True

LOG_LEVEL = "WARN"
LOG_TO_STDOUT = False
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']
