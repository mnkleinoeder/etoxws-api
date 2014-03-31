import os
import sys 

# if using ORACLE
# oracle_home = SETME (e.g., '/opt/oracle/client/product/11.2.0/client_1')
basepath = '/srv/www/webapps/etoxws-api'
sys.path.append(os.path.join(basepath, 'src'))

#rdkit_base = '/opt/rdkit/lib/python2.7/site-packages'
#sys.path.append(rdkit_base)

os.environ['DJANGO_SETTINGS_MODULE'] = 'etoxwsapi.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

