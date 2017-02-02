import hashlib
import logging
import requests
import json
import traceback
import time
from datetime import datetime

from etoxwsapi.v3 import schema

TIMEOUT = 120
SSL_VERIFY=False

def create_value_type_spec(spec):
    return	{
        "name": "value_type_spec",
        "type": "object",
        "properties": {
            "value" : spec,
        },
        "additionalProperties": False,
    }

def license_check(calc_info):
    #import pydevd; pydevd.settrace()
    is_valid = True
    infos = []
    license_infos = calc_info.get('license_infos', [])
    for li in license_infos:
        lic_end = li.get('license_end', 0)
        if 0 > lic_end:
            is_valid = False
            lic_stat = "License missing"
        elif 0 == lic_end:
            lic_stat = "Unrestricted license"
        else:
            lic_end_str = datetime.fromtimestamp(lic_end)
            if time.time() > lic_end:
                lic_stat = "Expired: %s"%(lic_end_str)
                is_valid = False
            else:
                lic_stat = "Valid until: %s"%(lic_end_str)

        _i = li.get('license_info', 'Required software')
        infos.append( _i + ' (' + lic_stat + ')' )

    if not license_infos:
        infos.append("No license information available")
         
    return is_valid, '|'.join(infos)

def modelid_from_calcinfo(provider, calc_info):
    return modelid(*(calc_info.get('id', None), provider, calc_info.get('version', None)))

def modelid(mtaxonomy, mprovider, mversion):
    '''
    as eTOXvault has no logical unique id per model in the DB design a hash is generated from the
    key logical entries in the record. Both a human readable tag and a hashed id is returned.

    returns tuple: (tag, hashid)
    '''
    mtag = None
    try:
        if mtaxonomy and mprovider and mversion:
            # very ugly hack to rectify wrong provider string
            _p = mprovider
            if mprovider == "Inte:Ligand GmbH":
                _p = 'IL'
            # making the clunky version info in etoxvault more tolerant
            _v = int(float(mversion))

            mtag = ':'.join([str(val).strip() for val in (mtaxonomy, _p, _v)])
    except Exception, e:
        logging.info("Could not generate modelid (%s, %s, %s): %s"%(mtaxonomy, mprovider, mversion, e))
    mid = hashlib.md5(str(mtag)).hexdigest()
    ret = (mtag, mid)
    return ret

def http_get(url, timeout=TIMEOUT):
    ret = requests.get(url, verify=SSL_VERIFY, timeout=TIMEOUT)

    if ret.status_code == 200:
        return ret
    else:
        logging.critical("Body of response:")
        logging.critical(ret.content)
        raise Exception("GET from '%s' failed with %s"%(url, ret.status_code))

class JobStatus(object):
    NONE = 0
    CRIT = 1
    WARN = 2
    INFO = 3
    def __init__(self, stat):
        self.stat = stat
        self.job_id = stat['job_id']

    def is_accepted(self):
        return (self.stat['status'] == "JOB_ACCEPTED")
    def is_running(self):
        return (self.stat['status'] == "JOB_RUNNING")

    def is_open(self):
        return not (self.is_done() or self.stat['status'] == "JOB_UNKNOWN")

    def is_done(self):
        return (self.stat['status'] in ( "JOB_COMPLETED", "JOB_SUCCESS", "JOB_FAILED", "JOB_REJECTED", "JOB_CANCELLED"))

    def is_success(self):
        return (self.stat['status'] in ( "JOB_COMPLETED", "JOB_SUCCESS"))

class JobSummary(JobStatus):
    def __init__(self, provider, baseurl, calc_info, stat):
        super(self.__class__, self).__init__(stat)
        self.provider = provider
        self.baseurl = baseurl
        self.calc_info = calc_info
        self.model_id = calc_info['id']
        self.name = "%s (version %s)"%(calc_info['id'], calc_info.get('version', '1'))
        self.summary = []

    def to_string(self, lev, linesep = '\n'):
        return linesep.join([m for l,m in self.summary if l == lev])

    def nmessage(self, lev):
        return len([s for s in self.summary if s[0] == lev])
    def success(self):
        return (self.nmessage(JobSummary.CRIT) == 0)


def submit_jobs(provider, baseurl, models, sdf_file, timeout = 60):
    """
    @param baseurl: base url of the webservice  
    @param models: list of calc_info objects
    @param sdf_file: string representation of the SDFile
    """
    calculation_request = schema.get('calculation_request')
    req_obj = calculation_request.create_object()

    req_obj.req_calculations = models

    req_obj.sdf_file = sdf_file

    req_ret = requests.post(baseurl+"/jobs/", data = req_obj.to_json(), verify=False,
                            headers={'Content-type': 'application/json'},
                            timeout=timeout)

    if req_ret.status_code == 200:
        jobs = []
        stats = json.loads(req_ret.text)
        if len(stats) != len(models):
            raise Exception("Number of started jobs does not match number of submitted models!")
        for i, stat in enumerate(stats):
            schema.validate(stat, schema.get('job_status'))
#				 self.summary.append((Job.CRIT, "%s; %s"%(e, stat)))
#				 logging.critical(str(e))
#				 logging.critical(calc_info)
#				 logging.critical(stat)

            jobs.append( JobSummary(provider, baseurl, models[i], stat) )
    else:
        raise Exception("Failed to submit jobs (%s): %s"%(req_ret.status_code, req_ret.text))
    return jobs

#def update_jobs(baseurl, jobs, timeout):
def update_jobs(jobs, timeout=TIMEOUT):
    for job in jobs:
        if job.is_done():
            continue
        url = '/'.join((job.baseurl, "jobs", job.job_id))
        try:
            ret = http_get(url, timeout=timeout)
            job.stat = ret.json()
        except Exception, e:
            logging.warn("Failed to update job status: %s (%s"%(url, e))

def make_prop_name(provider, calc_info, meta = ""):
    mid = calc_info['id']
    label, n = mid.split('/')[-2:]
    return "%s #%s (%s, v%s)%s"%(label, n, provider, calc_info.get('version', '1'), meta)

def extract_val(r, k1, k2, missing = None, icmp = None):
    val = 'n/a'
    avail = False
    try:
        if k2:
            val = r[k1][k2]
        else:
            val = r[k1]
        avail = True
    except KeyError:
        pass
    except Exception, e:
        print type(e)
        raise e
    if not avail and missing is not None:
        missing.append(icmp)
    return val


def analyze_job_results(jobs, sdfFile, update_sdf = True):
    def _missing(job, what, missing, nresults, thres = None):
        if len(missing) == 0:
            return
        lev = JobSummary.WARN
        nmissing = len(missing) 
        fail_ratio = (float(nmissing)/nresults)
        msg = "Prediction did not provide a %s for all compounds."%(what)
        if nmissing == nresults:
            msg += " Missing for all compounds!"
        elif nmissing > 10:
            msg += " Missing for more than %.2f %%"%( fail_ratio * 100 )
        else:
            msg += " Missing for records: %s"%( ','.join([str(tt) for tt in missing]) )
        if thres is not None:
            if fail_ratio > thres:
                lev = JobSummary.CRIT
        job.summary.append((lev, msg))

    for job in jobs:
        try:
            #import pydevd; pydevd.settrace()
            license_error = False
            ret = http_get('/'.join((job.baseurl, 'jobs', job.job_id)))
            if ret.status_code == 200:
                stat = json.loads(ret.text)
                job.stat = stat
                if job.is_success():
                    results = stat['results']

                    # clunky check for missing licenses. Message should be in the job status not in results
                    for r in results:
                        msg = r.get('message', None)
                        if msg and 'license' in msg.lower():
                            license_error = True
                            job.summary.append((JobSummary.CRIT, "No valid license."))
                    if license_error:
                        continue

                    if len(results) != len(sdfFile):
                        job.summary.append((JobSummary.CRIT, "Number of results (%s) does not match number of input compounds (%s)"%(len(results), len(sdfFile))))
                        continue

                    nresults = len(results)
                    val_missing = []
                    ad_missing = []
                    ri_missing = []
                    for r in results:
                        icmp = int(r['cmp_id'])
                        if r['success']:
                            val = extract_val(r, 'value', None,   val_missing, icmp)
                            ad  = extract_val(r, 'AD'   ,'value', ad_missing, icmp)
                            ri  = extract_val(r, 'RI'   ,'value', ri_missing, icmp)
                            if update_sdf:
                                sdfFile[icmp].add_prop( make_prop_name(job.provider, job.calc_info),         val)
                                sdfFile[icmp].add_prop( make_prop_name(job.provider, job.calc_info, ":ADAN"), ad)
                                sdfFile[icmp].add_prop( make_prop_name(job.provider, job.calc_info, ":RI"),   ri)
                            #pprint.pprint(r)
                        else:
                            val_missing.append(icmp)
                            job.summary.append((JobSummary.WARN, "Prediction failed for cpd #%s: %s"%(icmp, r.get('message', "Error message missing!"))))
                    
                    #_missing(job, "calculated value", val_missing, nresults, thres=0.5)
                    _missing(job, "calculated value", val_missing, nresults, thres=1.0)
                    _missing(job, "AD", ad_missing, nresults)
                    _missing(job, "RI", ri_missing, nresults)
                    #ad_missing, ri_missing
                else:
                    #job.summary.append((JobSummary.CRIT, "Job did not succeed successfully.\n%s:\n%s"%(stat['status'], results.get('msg', "No error message given") )))
                    job.summary.append((JobSummary.CRIT, "Job did not succeed successfully.\n%s:\n%s"%(stat['status'], stat.get('msg', "No error message given") )))
            else:
                job.summary.append((JobSummary.CRIT, "Failed to retrieve job status. HTTP status-code was '%s', returned data were: %s"%(ret.status_code, ret.text) ))
            
        except Exception, e:
            msg = "Failed to retrieve job status: %s\n"%(e)
            msg += "\n".join(traceback.format_exc().splitlines())

            job.summary.append((JobSummary.CRIT, msg))
