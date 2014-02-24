import json
from uuid import uuid1
import multiprocessing
import subprocess
import os
import socket
import sys
import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic.base import View

from etoxwsapi.v2 import schema

try:
	from django.conf import settings
	v2_impl = settings.ETOXWS_IMPL_V2()
except ImportError, e:
	print "Implementation for webservice v1 not found in settings_local.py"
	# TODO: error handling

from .models import Job, Result

class DummyLock():
	"""
	Dummy for running in sync mode w/ same parameters
	"""
	def acquire(self):
		pass
	def release(self):
		pass

class JobsView(View):
	def get(self, request):
		q = Job.objects.all()
		job_ids = [ j.job_id for j in q ]
		jsondata = json.dumps(job_ids)
		return HttpResponse(jsondata, mimetype='application/json')

	def post(self, request):
		logging.info("Calculation request from %s"%(request.META['REMOTE_ADDR']))
		job_status_schema = schema.get('job_status')
		calc_req_schema = schema.get('calculation_request')
		try:
			calc_request = calc_req_schema.loads(request.body)
			sdf_file = calc_request['sdf_file']
		except Exception, e:
			msg = "Invalid input data in request (%s)"%(e)
			return HttpResponse(msg, status = 500)
		
		job_stati = list()
		for calc_info in calc_request['req_calculations']:
			try:
				calc_info_schema = schema.get('calculation_info')
				calc_info_schema.validate(calc_info)
				job_id = uuid1().hex
				job = Job(start_time=0.0, job_id=job_id)
				job.save()
				job_status = job_status_schema.create_object(job_id=job_id, status="JOB_UNKNOWN")
				args = [job_id, calc_info, sdf_file]
				if settings.ETOXWS_IMPL_V2_ASYNC:
					args.append(multiprocessing.Lock())
					p = multiprocessing.Process(target=v2_impl.calculate, args=args)
					p.start()
				else:
					args.append(DummyLock())
					v2_impl.calculate(*args)
				job_status['status'] = "JOB_ACCEPTED"
			except Exception, e:
				job_status['msg'] = str(e)
				job_status['status'] = "JOB_REJECTED"
			job_stati.append(job_status)
		return HttpResponse(json.dumps(job_stati), mimetype='application/json')

class JobHandlerView(View):
	def get(self, request, job_id):
		try:
			job = Job.objects.get(job_id=job_id)

			job_status_schema = schema.get('job_status')
			job_status = job_status_schema.create_object()
			for key in job_status_schema.schema['properties'].keys():
				try:
					job_status[key] = getattr(job, key)
				except:
					pass
			if job.status == "JOB_COMPLETED":
				results = list()
				qs = Result.objects.filter(job=job).order_by('cmp_id')
				for q in qs:
					results.append(json.loads(q.result_json))
				job_status['results'] = results
			return HttpResponse(job_status.to_json())
		except Exception, e:
			msg = "Failed to retrieve job status (%s)"%(e)
			return HttpResponse(msg, status = 500)


	def delete(self, request, job_id):
		return HttpResponse("not yet implemented: cancelled job %s"%(job_id))
	
