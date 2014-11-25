# encoding: utf-8

import sys
import os

import requests
import time
from etoxwsapi.v2 import schema
import json
from pprint import pprint
import logging

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

#BASE_URL = 'http://192.168.56.100/etoxwsapi/v2'
BASE_URL = 'http://localhost:8001/etoxwsapi/v2'
#BASE_URL = 'http://192.168.178.217/etoxwsapi/v2'

def _get(url):
    ret = requests.get(url)

    if ret.status_code != 200:
        logging.debug("Body of response:")
        logging.debug(ret.content)
        raise Exception("GET from '%s' failed with %s"%(url, ret.status_code))
    return ret

def print_result(ids):
    frmt = '| %-7s | %-10s | %-10s | %-10s |'
    for (job_id,model_id) in ids:
        print "==========================================================================="
        print "Results for model '%s' (job: %s)\n"%(model_id, job_id)
        ret = requests.get('/'.join((BASE_URL, 'jobs', job_id)))
        if ret.status_code == 200:
            results = json.loads(ret.text)
            if results['status'] == "JOB_COMPLETED":
                print frmt%("cmp_id", "value", "AD", "RI")
                print '-' * len(frmt%('','','',''))
                for r in results['results']:
                    print frmt%(r['cmp_id'], r['value'], r['AD']['value'], r['RI']['value'])
            else:
                print "Job is not (yet) available: %s"%(results['status'])
        else:
            print "Could not get job results: %s, %s"%(ret.status_code, ret.text)

def submit_jobs(models):
    """
    preparing request for calculation
    """
    calculation_request = schema.get('calculation_request')
    req_obj = calculation_request.create_object()

    req_obj.req_calculations = models

    fname = os.path.join(THIS_DIR, "tiny.sdf")
    with open(fname) as fp:
        req_obj.sdf_file = fp.read()

    req_ret = requests.post(BASE_URL+"/jobs/", data = req_obj.to_json())

    if req_ret.status_code == 200:
        job_ids = list()
        for stat in json.loads(req_ret.text):
            job_ids.append(stat['job_id'])
            print "======================================================================"
            print "new job submitted."
            for t in ("job_id", "status"): #, "msg"):
                print "%s: %s"%(t, stat[t])
    else:
        raise Exception("Failed to submit jobs (%s): %s"%(req_ret.status_code, req_ret.text))

    return job_ids

def delete_job(job_id):
    ret = requests.delete(BASE_URL + '/jobs/' + job_id)
    print ret.status_code, ret.text

def observing_jobs(job_ids, interval = 5, duration = 0):
    print "Observing running jobs."
    if duration:
        print "Timeout: %d seconds"%(duration)
    poll = True
    i = 0
    while(poll):
        poll = False
        for job_id in job_ids:
            url = '/'.join((BASE_URL, "/jobs/%s"%(job_id)))
            ret = _get(url)
            stat = ret.json()
            print "status for '%s': %s"%(job_id, stat)
            if stat['status'] not in ( "JOB_COMPLETED", "JOB_FAILED", "JOB_REJECTED", "JOB_CANCELLED"):
                poll = True
        if duration > 0:
            i += interval
            if i >= duration:
                poll = False
        if poll:
            time.sleep(interval)

def main(argv=None):
    try:
        url = '/'.join((BASE_URL, 'dir'))
        ret = _get(url)

        models = [ m for m in json.loads(ret.text)]
        model_ids = [ model['id'] for model in models ]

        print "Available models"
        pprint(models)

        job_ids = submit_jobs(models)

        url = '/'.join((BASE_URL, 'jobs'))
        ret = _get(url)
        all_jobs = ret.json()
        
        for job_id in job_ids:
            assert(job_id in all_jobs)

        observing_jobs(job_ids)

        print_result(zip(job_ids, model_ids) )

    except Exception, e:
        print "Error occurred."
        print "%s"%(e)
        return 1
    return 0

if __name__ == "__main__":
    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(level=logging.WARN, format=FORMAT)
    sys.exit(main())
