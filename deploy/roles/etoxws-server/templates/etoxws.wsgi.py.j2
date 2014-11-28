import os
import sys 

basepath = '/srv/www/webapps/etoxws-api'
sys.path.append(os.path.join(basepath, 'src'))

# path to virtual env
sys.path.append('/opt/virtenv/etoxws-v2/lib/python2.6/site-packages')

#rdkit_base = '/opt/rdkit/lib/python2.7/site-packages'
#sys.path.append(rdkit_base)

os.environ['DJANGO_SETTINGS_MODULE'] = 'etoxwsapi.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#########################################################
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
  if not environ['PATH_INFO'].startswith(environ['SCRIPT_NAME']):
      environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']

  os.environ['WSGI_SCRIPT_NAME'] = environ['SCRIPT_NAME'] #os.environ and environ are different variables

  if environ['PATH_INFO'] == environ['SCRIPT_NAME']:
    environ['PATH_INFO']  += "/"

  return _application(environ, start_response)

