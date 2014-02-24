from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse

from etoxwsapi.v2 import schema

try:
	from django.conf import settings
	v2_impl = settings.ETOXWS_IMPL_V2()
except ImportError, e:
	print "Implementation for webservice v1 not found in settings_local.py"
	# TODO: error handling


def info(request):
	jsondata = v2_impl.info()
	return HttpResponse(jsondata, mimetype='application/json')

def dir(request):
	jsondata = v2_impl.dir()
	return HttpResponse(jsondata, mimetype='application/json')

