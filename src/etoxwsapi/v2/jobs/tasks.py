#import pydevd; pydevd.settrace()

import types

from etoxwsapi.djcelery import jobmgr

from django.conf import settings
from etoxwsapi.v2.jobs.models import Job
import time
v2_impl = settings.ETOXWS_IMPL_V2()

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class JobObserver():
    """
    This interface is used by WS implementations to communicate with the parent django application.
    As calculations will be performed in own threads this class provides thread-safe operations.
    
    Logging should only be done using the methods provided by this class.
    """
    def __init__(self, jobid, logger):
        self.job_id = jobid
        self.logger = logger
        self.results = dict()
        
        self.retcode = None
        self.msg = ""
        self.completion_time = 0

    def log_error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    def log_warn(self, msg, *args, **kwargs):
        self.logger.warn(msg, *args, **kwargs)
    def log_info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    def log_debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def _finalize(self):
        job = Job.objects.get(job_id=self.job_id)
        if self.retcode is None:
            stat = "JOB_UNKNOWN"
        elif self.retcode == 0:
            stat = "JOB_COMPLETED"
        else:
            stat = "JOB_FAILED"
        job.status = stat
        job.msg = self.msg
        job.completion_time = self.completion_time
        job.save()

    def report_progress(self, cur):
        """
        report progress: number of current record related to input sdfile
        """
        assert(type(cur) == types.IntType)
        job = Job.objects.get(job_id=self.job_id)
        job.currecord = cur
        job.status = "JOB_RUNNING"
        job.save()

    def report_status(self, retcode, errmsg):
        """
        after completion of calculation report the status:
        0 - success
        1 - failure
        """
        self.retcode = retcode
        self.msg = errmsg
        self.completion_time = time.time()

    def report_result(self, cmp_id, result_json):
        """
        give result for compound with cmp_id. result data must be given as JSON object with schema result_endpoint
        """
        self.results[cmp_id] = result_json
        from etoxwsapi.v2.jobs.models import Result
        job = Job.objects.get(job_id=self.job_id)
        result = Result(job=job, cmp_id=cmp_id, result_json=result_json)
        result.save()

@jobmgr.task(bind=True, name='etoxwsapi.v2.jobs.tasks.calculate')
def calculate(self, calc_info, sdf_file): #, logger, lock):
    #import pydevd; pydevd.settrace()
    jobid = self.request.id
    logger = get_task_logger("%s"%(jobid))
    logger.info("Starting calculation for %s"%(calc_info['id']))
    jr = JobObserver(jobid=jobid, logger=logger)
    try:
        v2_impl.calculate_impl(jr, calc_info, sdf_file)
    except Exception, e:
        jr.report_status(1, str(e))
    jr._finalize()