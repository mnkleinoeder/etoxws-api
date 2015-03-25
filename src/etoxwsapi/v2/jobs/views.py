import json
from uuid import uuid1
import logging
import time

from django.http import HttpResponse
#from django.shortcuts import render_to_response, render
from django.views.generic.base import View

from etoxwsapi.v2 import schema

from .models import Job, Result

from cStringIO import StringIO

#from etoxwsapi.v2.jobs import tasks
import etoxwsapi.v2.jobs.tasks
from celery.result import AsyncResult
from etoxwsapi.djcelery import jobmgr
import sys
import traceback
from django.shortcuts import get_object_or_404
import os
import psutil

logger = logging.getLogger(__name__)

# celery status codes:
#PENDING
#STARTED
#SUCCESS
#FAILURE
#RETRY
#REVOKED

# API status codes:
#"JOB_UNKNOWN",
#"JOB_REJECTED",
#"JOB_ACCEPTED",
#"JOB_RUNNING",
#"JOB_COMPLETED",
#"JOB_FAILED",
#"JOB_CANCELLED"

def _map_state(cel_state):
    if cel_state in ["PENDING", "RETRY", "STARTED"]:
        return "JOB_ACCEPTED"
    elif cel_state == "SUCCESS":
        return "JOB_COMPLETED"
    elif cel_state == "FAILURE":
        return "JOB_FAILED"
    elif cel_state == "REVOKED":
        return "JOB_CANCELLED"
    else:
        return "JOB_UNKNOWN"

def _conv_job(job):
    job_status_schema = schema.get('job_status')
    job_status = job_status_schema.create_object()
    for key in job_status_schema.schema['properties'].keys():
        if key in ( "results", "calculation_info" ):
            # results are stored in a separate DB table
            continue
        try:
            job_status[key] = getattr(job, key)
        except Exception, e:
            logger.error("Job attribute missing: %s"%(e))
    if job.status == "JOB_COMPLETED":
        results = list()
        qs = Result.objects.filter(job=job).order_by('cmp_id')
        for q in qs:
            results.append(json.loads(q.result_json))
        job_status['results'] = results
    return job_status

def _nrecord(sdf_file):
    nrec = 0
    for line in StringIO(sdf_file):
        if line[0] == 'M' and line.startswith("M  END"):
            nrec += 1
    return nrec

def _wrap_method(method, request):
    try:
        return method(request)
    except Exception:
        msg = json.dumps(traceback.format_exc().splitlines())
        return HttpResponse(msg, status = 500, content_type='application/json')

class JobsView(View):
    def post(self, request):
        return _wrap_method(self._post, request)
    def get(self, request):
        return _wrap_method(self._get, request)

    def _get(self, request):
        q = Job.objects.all()
        job_ids = [ j.job_id for j in q ]
        jsondata = json.dumps(job_ids)
        request.META["CSRF_COOKIE_USED"] = True
        return HttpResponse(jsondata, content_type='application/json')

    def _post(self, request):
        logger.info("Calculation request from %s"%(request.META['REMOTE_ADDR']))
        calc_req_schema = schema.get('calculation_request')
        try:
            calc_request = calc_req_schema.loads(request.body)
            sdf_file = calc_request['sdf_file']
            nrecord = _nrecord(sdf_file)
        except Exception, e:
            msg = "Invalid input data in request (%s)"%(e)
            return HttpResponse(msg, status = 400)

        jobs = list()
        for calc_info in calc_request['req_calculations']:
            cjob = None
            job_id = unicode(uuid1())
            job = Job(start_time=time.time(), job_id=job_id, status="JOB_UNKNOWN", nrecord=nrecord)
            job.save()
            try:
                logger.info("Submitting job for '%s': %s"%(calc_info['id'], job_id))
                calc_info_schema = schema.get('calculation_info')
                calc_info_schema.validate(calc_info)

                cjob = etoxwsapi.v2.jobs.tasks.calculate.apply_async((calc_info, sdf_file), task_id=job_id, retry=False)  #@UndefinedVariable

                job.status = _map_state(cjob.state)
            except Exception, e:
                try:
                    cjob.revoke()
                except Exception, ee:
                    logging.warn("Error while trying to revoke failed job: %s"%(ee))
                job.completion_time = time.time()
                job.msg = str(e)
                job.status = "JOB_REJECTED"
                logger.warn("Failed submission of '%s': %s"%(calc_info['id'], e))
                job.save()

            jobs.append(_conv_job(job))

        return HttpResponse(json.dumps(jobs), content_type='application/json')

class JobHandlerView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, job_id=job_id)
        try:
            job_status = _conv_job(job)
            
            if job_status['status'] == "JOB_UNKNOWN":
                try:
                    cjob = AsyncResult(job_id)
                    job_status['status'] = _map_state(cjob.state)
                except Exception, e:
                    logger.warn("Failed to query celery for job: %s (%s)"%(job_id, e))

            return HttpResponse(job_status.to_json())
        except Exception, e:
            msg = "Failed to retrieve job status (%s)"%(e)
            return HttpResponse(msg, status = 500)

    def delete(self, request, job_id):
        job = get_object_or_404(Job, job_id=job_id)
        try:
            logger.info("Entering DELETE for job: %s"%(job_id))
            #import pydevd; pydevd.settrace('192.168.0.234')
            cjob = AsyncResult(job_id)
            if not cjob.ready():
                if job.pid > 0:
                    logger.info("Trying to kill job subprocess and all children: %s"%(job_id))
                    try:
                        parent = psutil.Process(job.pid)
                        logger.info("Command line was: %s (%s)"%(parent.cmdline(), parent.pid))
                        for child in parent.children(recursive=True):
                            try:
                                logger.info("Found child process: %s (%s)"%(child.cmdline(), child.pid))
                                child.kill()
                            except Exception, e:
                                logger.warn("%s"%(e))
                        parent.kill()
                    except Exception, e:
                        logger.warn("%s"%(e))
                jobmgr.control.revoke(job_id, terminate=True) #@UndefinedVariable
                job.status = "JOB_CANCELLED"
                job.completion_time = time.time()
                job.save()
            return HttpResponse("", status = 200)
        except Exception, e:
            msg = "Failed to delete job (%s)"%(e)
            return HttpResponse(msg, status = 500)

