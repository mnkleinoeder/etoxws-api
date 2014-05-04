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

def _get_db_job(job_id):
	# TODO: error handling
	from etoxwsapi.v2.jobs.models import Job
	job = Job.objects.get(job_id=job_id)
	return job

def _save_db_obj(obj, lock):
	lock.acquire()
	obj.save()
	lock.release()

class JobObserver():
	"""
	This interface is used by WS implementations to communicate with the parent django application.
	As calculations will be performed in own threads this class provides thread-safe operations.
	
	Logging should only be done using the methods provided by this class.
	"""
	def __init__(self, jid, lock, logger):
		self.job_id = jid
		self.lock = lock
		self.logger = logger

	def log_error(self, msg, *args, **kwargs):
		"""
		log critical error event
		"""
		self.lock.acquire()
		self.logger.error(*args)
		self.lock.release()

	def log_warn(self, msg, *args, **kwargs):
		"""
		log warning (not critical)
		"""
		self.lock.acquire()
		self.logger.warn(msg, *args, **kwargs)
		self.lock.release()

	def log_info(self, msg, *args, **kwargs):
		"""
		give additional information about calculation details
		"""
		self.lock.acquire()
		self.logger.info(msg, *args, **kwargs)
		self.lock.release()

	def log_debug(self, msg, *args, **kwargs):
		"""
		give debug information (for development purpose)
		"""
		self.lock.acquire()
		self.logger.debug(msg, *args, **kwargs)
		self.lock.release()

	def report_progress(self, cur):
		"""
		report progress: number of current record related to input sdfile
		"""
		assert(type(cur) == types.IntType)
		job = _get_db_job(self.job_id)
		job.currecord = cur
		_save_db_obj(job, self.lock)

	def report_status(self, retcode, errmsg):
		"""
		after completion of calculation report the status:
		0 - success
		1 - failure
		"""
		job = _get_db_job(self.job_id)
		if retcode == 0:
			stat = "JOB_COMPLETED"
		else:
			stat = "JOB_FAILED"
		job.status = stat
		job.msg = errmsg
		_save_db_obj(job, self.lock)

	def report_result(self, cmp_id, result_json):
		"""
		give result for compound with cmp_id. result data must be given as JSON object with schema result_endpoint
		"""
		from etoxwsapi.v2.jobs.models import Result
		job = _get_db_job(self.job_id)
		result = Result(job=job, cmp_id=cmp_id, result_json=result_json)
		_save_db_obj(result, self.lock)

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
	def calculate(self, job_id, calc_info, sdf_file, logger, lock):
		logger.debug("Preparing job")
		jr = JobObserver(job_id, lock, logger)
		job = _get_db_job(job_id)
		job.pid = os.getpid()
		job.start_time = time.time()
		job.nrecord = self._nrecord(sdf_file)
		job.calculation_info = calc_info
		job.status = "JOB_RUNNING"
		_save_db_obj(job, lock)
		
		logger.info("handing over control to webservice implementation")
		try:
			self.calculate_impl(jr, calc_info, sdf_file)
			logger.info("calculation successfully finished")
		except Exception, e:
			logger.error("calculate_impl exception: %s\n%s"%(e, traceback.format_exc()))
			jr.report_status(1, str(e))

		job = _get_db_job(job_id)
		job.completion_time = time.time()
		_save_db_obj(job, lock)







