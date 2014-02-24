import json
import os
import tempfile
from cStringIO import StringIO
import subprocess
import logging
import json

from etoxwsapi.v1.wsbase import WebserviceImplementationBase

_AVAILABLE_PREDICTIONS = [ "/endpoint/definition/model/1" ]

class WS1(WebserviceImplementationBase):
	def info(self):
		data = { "provider": "Sample Organization",
							"homepage": "http://www.example.com",
							"admin": "Jim Admin",
							"admin-email": "admin@example.com"
							}
		return json.dumps(data)

	def available_services(self):
		data = { "predictions": _AVAILABLE_PREDICTIONS}
		return json.dumps(data)
	

	def calculate(self, file, format, property):
	#	v1_impl.calculate(file, format, property)
		logging.info("Running models for %s (input format: %s)"%(property, format))
		results = {}
		logging.info("Succeeded.")
		return json.dumps(results)
		
# def _calc_for_compound(property, record):
# 	value = 123.45
# 	if property == "DIPL1":
# 		pass # apply your model
# 	elif property == "CACO2":
# 		pass # apply your model
# 		
# 	return value
# 
# def _calculate_in_memory(file, format, property):
# 	results = list()
# 	buffer = StringIO()
# 	for line in file:
# 		buffer.write(line)
# 		if format == "SMILES" or (format == "SDF" and line.startswith("$$$$")):
# 			record = buffer.getvalue()
# 			buffer = StringIO()
# 			try:
# 				val = _calc_for_compound(property, record)
# 				stat = 0
# 				msg = ""
# 			except Exception, e:
# 				val = None
# 				stat = 1
# 				msg = str(e)
# 			results.append((val, stat, msg))
# 	return results
# 
# def _write_tmpfile(file, format):
# 	tmpfile = tempfile.mktemp(suffix=".%s"%(format.lower()))
# 	fh = open(tmpfile, "wb")
# 	for chunk in file.chunks():
# 		fh.write(chunk)
# 	fh.close()
# 	return tmpfile
# 
# def _calculate_external(file, format, property):
# 	results = list()
# 	tmpfile = _write_tmpfile(file, format)
# 
# 	# create
# 	cmd = [ 'grep', '$$$$', tmpfile ]
# 	try:
# 		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# 		result, errors = p.communicate()
# 		if p.returncode != 0:
# 			raise Exception, errors
# 		results.extend([(r, 0, '') for r in result.split()])
# 	except Exception, e:
# 		raise Exception, "Error while running command '%s': '%s'"%(cmd, e)
# 
# 	os.unlink(tmpfile)
# 
# 	return results
# 
# @csrf_exempt
# def calculate(request):
# 	logging.info("Calculation request from %s"%(request.META['REMOTE_ADDR']))
# 	property = str()
# 	results = list()
# 	msg = str()
# 	status_code = 200
# 
# 	try:
# 		if request.method != 'POST':
# 			raise Exception, "Only HTTP POST is supported"
# 		indata = request.POST
# 		if (len(request.FILES) != 1):
# 			raise Exception, "One input file required in uploaded data"
# 
# 		property = indata['property']
# 		if not property in _AVAILABLE_PREDICTIONS:
# 			raise Exception, "Unknown property: '%s'"%(property)
# 		format = indata['format']
# 		if not format in _SUPPORTED_FILE_FORMATS:	
# 			raise Exception, "Unknown file format: '%s'"%(format)
# 
# 		file = request.FILES['uploadfile']
# 
# 		logging.info("Running models for %s (input format: %s)"%(property, format))
# 		results.extend(_calculate_in_memory(file, format, property))
# 		results.extend(_calculate_external(file, format, property))
# 		logging.info("Succeeded.")
# 	except Exception, e:
# 		status_code = 500
# 		msg = str(e)
# 		logging.error("Failed: %s"%(msg))
# 
# 	jsondata = dict()
# 	jsondata["property"] = property
# 	jsondata["results"] = results
# 	jsondata["msg"] = msg
# 
# 	json = simplejson.dumps(jsondata)
# 	return HttpResponse(json, mimetype='application/json', status=status_code)
# 
# if __name__ == '__main__':
# 	from django.test.client import Client
# 	#Note : one could use RequestFactory instead of Client
# 	# advantage: it does not use the url defined in urls.py 
# 	
# 	client = Client()
# 	print client.post('/info')
# 	print client.post('/dir')
# 	
# 	data = {'uploadfile': open('tiny.sdf'), 'format': 'SDF', 'property': 'DIPL1' }
# 	response = client.post('/calculate', data)
# 	print response.status_code, response

