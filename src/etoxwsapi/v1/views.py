import json

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

try:
	from django.conf import settings
	v1_impl = settings.ETOXWS_IMPL_V1()
except ImportError, e:
	print "Implementation for webservice v1 not found in settings_local.py"
	# TODO: error handling

@csrf_exempt
def info(request):
	try:
		jsondata = v1_impl.info()
		return HttpResponse(jsondata, content_type='application/json')
	except Exception, e:
		raise 

@csrf_exempt
def available_services(request):
	jsondata = v1_impl.dir()
	return HttpResponse(jsondata, content_type='application/json')

@csrf_exempt
def calculate(request):
	property = 'n/a'
	try:
		if request.method != 'POST':
			raise Exception, "Only HTTP POST is supported"
		indata = request.POST
		if (len(request.FILES) != 1):
			raise Exception, "One input file required in uploaded data"

		property = indata['property']
		if not property in v1_impl._AVAILABLE_PREDICTIONS:
			raise Exception, "Unknown property: '%s'"%(property)
		format = indata['format']
		if not format in ('sdf', 'mol'):	
			raise Exception, "Unknown file format: '%s'"%(format)

		file = request.FILES['uploadfile']

		jsondata = v1_impl.calculate(file, format, property)
		status_code = 200
	except Exception, e:
		jsondata = json.dumps({"property" : property, "results": "", "msg":  str(e) })
		status_code = 500
	return HttpResponse(jsondata, content_type='application/json', status=status_code)

