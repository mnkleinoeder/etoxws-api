from .base import *  # @UnusedWildImport

DEBUG = True

BROKER_URL = 'amqp://etoxwsapi_dev:etoxwsapi@localhost:5672/etoxwsapi_dev'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "etoxwsapi_dev",
        'USER': "etoxwsapi_dev",
        'PASSWORD': "etoxwsapi_dev"
    }
}

#sys.path.append('/home/thomas/git/etoxws-MN/src/wsimpl_v2')

from sampleimpl.ws_impl_v1 import WS1
from sampleimpl.ws_impl_v2 import WS2
#from broker import WS2

ETOXWS_IMPL_V1 = WS1
ETOXWS_IMPL_V2 = WS2

ETOXWS_IMPL_V2_ASYNC = True

LOG_LEVEL = "INFO"

LOG_TO_STDOUT = True

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

