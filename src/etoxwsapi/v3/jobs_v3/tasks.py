#import pydevd; pydevd.settrace()

import types
import time
import traceback
from StringIO import StringIO
from django.conf import settings

from etoxwsapi.djcelery import jobmgr
from etoxwsapi.utils import SDFFile

from etoxwsapi.v3.jobs_v3.models import Job

v3_impl_cls = settings.ETOXWS_IMPL_V3

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
        
        self.retcode = -1
        self.msg = ""
        self.completion_time = 0
        self.offset = 0

    def _log(self, func, msg, *args, **kwargs):
        if not msg:
            return
        func(msg, *args, **kwargs)
        
    def log_error(self, msg, *args, **kwargs):
        self._log(self.logger.error, msg, *args, **kwargs)
    def log_warn(self, msg, *args, **kwargs):
        self._log(self.logger.warn, msg, *args, **kwargs)
    def log_info(self, msg, *args, **kwargs):
        self._log(self.logger.info, msg, *args, **kwargs)
    def log_debug(self, msg, *args, **kwargs):
        self._log(self.logger.debug, msg, *args, **kwargs)

    def _finalize(self):
        job = Job.objects.get(job_id=self.job_id)
        if self.retcode == 0:
            stat = "JOB_SUCCESS"
        else:
            stat = "JOB_FAILED"
        job.status = stat
        job.msg = self.msg
        job.completion_time = self.completion_time
        job.save()

    def is_valid(self):
        job = Job.objects.get(job_id=self.job_id)
        self.log_info(job.status)
        return self.retcode == 0 and ("JOB_CANCELLED" != job.status)
        
    def report_progress(self, current_record):
        """
        report progress: number of current record related to input sdfile
        """
        assert(type(current_record) == types.IntType)
        job = Job.objects.get(job_id=self.job_id)
        job.currecord = current_record + self.offset
        job.status = "JOB_RUNNING"
        job.save()

    def report_started(self, pid=None):
        """
        indicate that the calculation has started. If an external program has been started by
        subprocess submit the pid as argument.
        """
        
        job = Job.objects.get(job_id=self.job_id)
        job.status = "JOB_RUNNING"
        if pid:
            job.pid = pid
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
        i =  cmp_id + self.offset
        self.results[i] = result_json
        from etoxwsapi.v3.jobs_v3.models import Result
        job = Job.objects.get(job_id=self.job_id)
        result = Result(job=job, cmp_id=i, result_json=result_json)
        result.save()

@jobmgr.task(bind=True, ignore_result=True, name='etoxwsapi.v3.jobs_v3.tasks.calculate')
def calculate(self, calc_info, sdf_file): #, logger, lock):
    #import pydevd; pydevd.settrace()
    jobid = self.request.id
    logger = get_task_logger("%s"%(jobid))
    logger.info("Starting calculation for %s"%(calc_info['id']))
    jr = JobObserver(jobid=jobid, logger=logger)
    try:
        v3_impl = v3_impl_cls()
        chunk_size = 100
        sdf = SDFFile(StringIO(sdf_file))
        chunks = sdf.split(chunk_size)
        for i, chunk in enumerate(chunks):
            logger.info("Processing chunk %s/%s (chunksize is %s)"%(i+1, len(chunks), chunk_size))
            jr.offset = chunk_size*i
            v3_impl.calculate_impl(jr, calc_info, chunk.to_string())
            if not jr.is_valid():
                break
    except Exception, e:
        logger.error("Exception occurred: %s"%(e))
        msg = str(e) + '\n' + '\n'.join(traceback.format_exc().splitlines())
        logger.error(msg)
        jr.report_status(1, msg)
    jr._finalize()
