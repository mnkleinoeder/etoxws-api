import json
import os
import tempfile
from cStringIO import StringIO
import subprocess
import logging
import json

from etoxwsapi.v1.wsbase import WebserviceImplementationBase

class WS1(WebserviceImplementationBase):
	_AVAILABLE_PREDICTIONS = [ "/endpoint/definition/model/1" ]
	def info(self):
		data = { "provider": "Sample Organization",
							"homepage": "http://www.example.com",
							"admin": "Jim Admin",
							"admin-email": "admin@example.com"
							}
		return json.dumps(data)

	def available_services(self):
		data = { "predictions": self._AVAILABLE_PREDICTIONS}
		return json.dumps(data)
	

	def calculate(self, file, format, property):
	#	v1_impl.calculate(file, format, property)
		logging.info("Running models for %s (input format: %s)"%(property, format))
		results = {}
		logging.info("Succeeded.")
		return json.dumps(results)
		
