import types
import subprocess
import os
import sys
import json
import logging
import time
from cStringIO import StringIO

from etoxwsapi.v2 import schema
import traceback


# TODO: make this an interface
class WebserviceImplementationBase(object):
	"""
	Adapter class to connect the webservice application with the implementation.
	This class needs to be subclassed and the *_impl() methods need to be redefined. 
	"""
	def __init__(self):
		pass

	def info_impl(self):
		"""
		Concrete implementations need to return a ws_info JSON object
		"""
		raise NotImplementedError("must be implemented by subclass")
	def info(self):
		return self.info_impl()

	def dir_impl(self):
		"""
		Needs to return an array of calculation_info JSON objects
		"""
		raise NotImplementedError("must be implemented by subclass")
	def dir(self):
		retval = self.dir_impl()
		from django.conf import settings
		if settings.DEBUG:
			# also for WS with only one model we expect an list of calc_infos
			assert(isinstance(json.loads(retval), types.ListType))
		return retval

	def _nrecord(self, sdf_file):
		nrec = 0
		for line in StringIO(sdf_file):
			if line[0] == 'M' and line.startswith("M  END"):
				nrec += 1
		return nrec
		
	def calculate_impl(self, jobobserver, calc_info, sdf_file):
		"""
		Implements the calculation. Use the jobobserver to report calculation progress,
		submit results and issue logging messages.
		"""
		raise NotImplementedError("must be implemented by subclass")
#	def calculate(self, job_id, calc_info, sdf_file, logger, lock):
#		logger.debug("preparing job")
#		jr = jobobserver(job_id, lock, logger)
#		job = _get_db_job(job_id)
#		job.pid = os.getpid()
#		job.start_time = time.time()
#		job.nrecord = self._nrecord(sdf_file)
#		job.calculation_info = calc_info
#		job.status = "job_running"
#		_save_db_obj(job, lock)
#		
#		logger.info("handing over control to webservice implementation")
#		try:
#			self.calculate_impl(jr, calc_info, sdf_file)
#			logger.info("calculation successfully finished")
#		except exception, e:
#			logger.error("calculate_impl exception: %s\n%s"%(e, traceback.format_exc()))
#			jr.report_status(1, str(e))
#
#		job = _get_db_job(job_id)
#		job.completion_time = time.time()
#		_save_db_obj(job, lock)







