import json
from uuid import uuid1
import multiprocessing
import subprocess
import os
import socket
import sys
import logging
import time
import signal

from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic.base import View
from django.http.response import Http404
from django.middleware import csrf
from django.conf import settings

from etoxwsapi.v2 import schema

from .models import Job, Result

from cStringIO import StringIO

#from etoxwsapi.v2.jobs import tasks
import etoxwsapi.v2.jobs.tasks

logger = logging.getLogger(__name__)

class DummyLock():
    """
    Dummy for running in sync mode w/ same parameters
    """
    def acquire(self):
        pass
    def release(self):
        pass

#PENDING
#STARTED
#SUCCESS
#FAILURE
#RETRY
#REVOKED

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

def _from_job_status(job_status):
    pass

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

class JobInfo:
    def __init__(self, ci):
        self.calc_info = ci
        self.msg = ""
        self.cjob = None


class JobsView(View):
    def get(self, request):
        q = Job.objects.all()
        job_ids = [ j.job_id for j in q ]
        jsondata = json.dumps(job_ids)
        request.META["CSRF_COOKIE_USED"] = True
        return HttpResponse(jsondata, content_type='application/json')

    def post(self, request):
        logger.info("Calculation request from %s"%(request.META['REMOTE_ADDR']))
        calc_req_schema = schema.get('calculation_request')
        job_status_schema = schema.get('job_status')
        try:
            calc_request = calc_req_schema.loads(request.body)
            sdf_file = calc_request['sdf_file']
        except Exception, e:
            msg = "Invalid input data in request (%s)"%(e)
            return HttpResponse(msg, status = 400)

        jobs = list()
        for calc_info in calc_request['req_calculations']:
            jobinfo = JobInfo(calc_info)
            try:
#				logger.info("Submitting job for '%s': %s"%(calc_info['id'], job_id))
                calc_info_schema = schema.get('calculation_info')
                calc_info_schema.validate(calc_info)

                cjob = etoxwsapi.v2.jobs.tasks.calculate.delay(calc_info, sdf_file)  #@UndefinedVariable
                jobinfo.cjob = cjob
            except Exception, e:
#                job.completion_time = time.time()
                jobinfo.msg = str(e)
                logger.warn("Failed submission of '%s': %s"%(calc_info['id'], e))
            jobs.append(jobinfo)

                
#                job_status["status"] = job_state
#				logger.info("OK: submission of '%s': %s"%(calc_info['id'], job_id))
#            job_stati.append(job_status)
        
        job_stati = list()
        for jobinfo in jobs:
            job_status = job_status_schema.create_object(job_id="-1", status="JOB_UNKNOWN", calculation_info=jobinfo.calc_info)
            if jobinfo.cjob is None:
                job_status['status'] = 'JOB_REJECTED'
                job_status['msg'] = jobinfo.msg
            else:
                while(True):
                    try:
                        job = Job.objects.get(job_id=jobinfo.cjob.id)
                        job_status = _conv_job(job)
                        break
                    except Job.DoesNotExist:
                        time.sleep(1)
            job_stati.append(job_status)
            
        return HttpResponse(json.dumps(job_stati), content_type='application/json')

class JobHandlerView(View):
    def get(self, request, job_id):
        try:
            job = Job.objects.get(job_id=job_id)
            job_status = _conv_job(job)

#            job_status_schema = schema.get('job_status')
#            job_status = job_status_schema.create_object()
#            for key in job_status_schema.schema['properties'].keys():
#                if key in ( "results", "calculation_info" ):
#                    # results are stored in a separate DB table
#                    continue
#                try:
#                    job_status[key] = getattr(job, key)
#                except Exception, e:
#                    logger.error("Job attribute missing: %s"%(e))
#            if job.status == "JOB_COMPLETED":
#                results = list()
#                qs = Result.objects.filter(job=job).order_by('cmp_id')
#                for q in qs:
#                    results.append(json.loads(q.result_json))
#                job_status['results'] = results
            return HttpResponse(job_status.to_json())
        except Job.DoesNotExist:
            return HttpResponse("job_id '%s' not existent"%(job_id), status = 404)
        except Exception, e:
            msg = "Failed to retrieve job status (%s)"%(e)
            return HttpResponse(msg, status = 500)


    def delete(self, request, job_id):
        try:
            job = Job.objects.get(job_id=job_id)
            try:
                print "killing job", job.pid
                os.kill(job.pid, signal.SIGKILL)
            except OSError, e:
                logger.warn("Failed to kill job: %s (job_id: %s)"%(e, job_id))

            job.status = "JOB_CANCELLED"
            job.completion_time = time.time()
            job.save()
            return HttpResponse("", status = 200)

        except Job.DoesNotExist:
            return HttpResponse("job_id '%s' not existent"%(job_id), status = 404)
        except Exception, e:
            msg = "Failed to delete job (%s)"%(e)
            return HttpResponse(msg, status = 500)
