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
	def __init__(self, jid, lock, logger):
		self.job_id = jid
		self.lock = lock
		self.logger = logger

	def log_error(self, *args):
		self.lock.acquire()
		self.logger.error(*args)
		self.lock.release()

	def log_warn(self, *args):
		self.lock.acquire()
		self.logger.warn(*args)
		self.lock.release()

	def log_info(self, *args):
		self.lock.acquire()
		self.logger.info(*args)
		self.lock.release()

	def log_debug(self, *args):
		self.lock.acquire()
		self.logger.debug(*args)
		self.lock.release()

	def report_progress(self, cur):
		assert(type(cur) == types.IntType)
		job = _get_db_job(self.job_id)
		job.currecord = cur
		_save_db_obj(job, self.lock)

	def report_status(self, retcode, errmsg):
		job = _get_db_job(self.job_id)
		if retcode == 0:
			stat = "JOB_COMPLETED"
		else:
			stat = "JOB_FAILED"
		job.status = stat
		job.msg = errmsg
		_save_db_obj(job, self.lock)

	def report_result(self, cmp_id, result_json):
		from etoxwsapi.v2.jobs.models import Result
		job = _get_db_job(self.job_id)
		result = Result(job=job, cmp_id=cmp_id, result_json=result_json)
		_save_db_obj(result, self.lock)

# TODO: make this an interface
class WebserviceImplementationBase(object):
	def __init__(self):
		pass

	def info_impl(self):
		raise NotImplementedError("must be implemented by subclass")
	def info(self):
		return self.info_impl()

	def dir_impl(self):
		raise NotImplementedError("must be implemented by subclass")
	def dir(self):
		retval = self.dir_impl()
		from django.conf import settings
		if settings.DEBUG:
			assert(isinstance(json.loads(retval), types.ListType))
		return retval

	def _nrecord(self, sdf_file):
		nrec = 0
		for line in StringIO(sdf_file):
			if '$$$$' in line:
				nrec += 1
		return nrec
		
	def calculate_impl(self, observer, file, property):
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







