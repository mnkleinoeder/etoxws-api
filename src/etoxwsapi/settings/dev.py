from .base import *  # @UnusedWildImport
import socket

DEBUG = True
TEMPLATE_DEBUG = True

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


