# encoding: utf-8

import sys
import os

import requests
import time
from etoxwsapi.v2 import schema
import json
import pprint
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_FILE = os.path.join(THIS_DIR, "tiny.sdf")
BASE_URL = 'https://localhost/etoxwsapi/v2'
LOG_LEV = "WARN"
SSL_VERIFY=False

_POLL_INTERVALL = 5
_DURATION = -1
_DELETE_AFTER = -1

def _get(url):
    ret = requests.get(url, verify=SSL_VERIFY)

    if ret.status_code == 200:
        return ret
    else:
        logging.critical("Body of response:")
        logging.critical(ret.content)
        raise Exception("GET from '%s' failed with %s"%(url, ret.status_code))

def _val(r, k1, k2 = None):
    try:
        if k2:
            return r[k1][k2]
        else:
            return r[k1]
    except KeyError:
        return 'no value!'
    except Exception, e:
        print type(e)
        raise e

def print_result(ids):
    frmt = '| %-7s | %-10s | %-10s | %-10s |'
    for (job_id,model_id) in ids:
        print "==========================================================================="
        print "Results for model '%s' (job: %s)\n"%(model_id, job_id)
        ret = _get('/'.join((BASE_URL, 'jobs', job_id)))
        if ret.status_code == 200:
            results = json.loads(ret.text)
            if results['status'] == "JOB_COMPLETED":
                print frmt%("cmp_id", "value", "AD", "RI")
                print '-' * len(frmt%('','','',''))
                for r in results['results']:
                    print frmt%(_val(r, 'cmp_id'), _val(r, 'value'), _val(r, 'AD','value'), _val(r, 'RI','value'))
            else:
                print "Job is not (yet) available: %s (%s)"%(results['status'], results['msg'])
        else:
            print "Could not get job results: %s, %s"%(ret.status_code, ret.text)

def submit_jobs(models):
    """
    preparing request for calculation
    """
    calculation_request = schema.get('calculation_request')
    req_obj = calculation_request.create_object()

    req_obj.req_calculations = models

    fname = TEST_FILE
    with open(fname) as fp:
        req_obj.sdf_file = fp.read()

    req_ret = requests.post(BASE_URL+"/jobs/", data = req_obj.to_json(), verify=SSL_VERIFY)

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
    ret = requests.delete(BASE_URL + '/jobs/' + job_id, verify=SSL_VERIFY)
    print ret.status_code, ret.text

def observing_jobs(job_ids, interval, duration, cancel_after):
    print "Observing running jobs."
    if duration:
        print "Timeout: %d seconds"%(duration)
    poll = True
    i = 0
    while(poll):
        poll = False
        for job_id in job_ids:
            if i == cancel_after:
                delete_job(job_id)
            url = '/'.join((BASE_URL, "/jobs/%s"%(job_id)))
            ret = _get(url)
            stat = ret.json()
            print "status for '%s': %s (progress: %s/%s)"%(job_id, stat['status'], stat['currecord'], stat['nrecord'])
            logging.debug(stat)
            if stat['status'] not in ( "JOB_COMPLETED", "JOB_FAILED", "JOB_REJECTED", "JOB_CANCELLED"):
                poll = True
        i += 1
        if duration > 0:
            if i*interval >= duration:
                poll = False
        if poll:
            time.sleep(interval)

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None):
    program_name = os.path.basename(sys.argv[0])

    global BASE_URL, LOG_LEV, TEST_FILE
    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-b", "--base-url", dest="baseurl", help="base url of webservice to be tested [default: %(default)s]", default=BASE_URL)
        parser.add_argument("-i", "--ids", dest="ids", help="comma-separated list with IDs to be calculated [default: all, as obtained by /dir]", default=None)
        parser.add_argument("-l", "--log-level", dest="loglev", help="set verbosity level [default: %(default)s] (see python logging module)", default=LOG_LEV)
        parser.add_argument("-t", "--test-file", dest="testfile", help="SDFile to be used for the test run. [default: %(default)s]", default=TEST_FILE )
        parser.add_argument("-p", "--poll-interval", dest="poll", type=int, help="poll status each N sec [default: %(default)s]", metavar="N", default= _POLL_INTERVALL)
        parser.add_argument("-d", "--duration", dest="duration", type=int, help="stop this program after N sec [default: %(default)s]", metavar="N", default= _DURATION)
        parser.add_argument("-c", "--delete-after", dest="delete", type=int, help="issue a DELETE request after N polls [default: %(default)s]", metavar="N", default= _DELETE_AFTER)
        parser.add_argument("-n", "--dry-run", action='store_true', help="don't trigger calculation")

        # Process arguments
        args = parser.parse_args()

        FORMAT = "%(levelname)s: %(message)s"
        logging.basicConfig(level=logging.getLevelName(args.loglev), format=FORMAT)

        BASE_URL = args.baseurl
        TEST_FILE = args.testfile

        #import pydevd; pydevd.settrace()
        ids = list()
        try:
            ids = args.ids.split(',')
        except Exception, e:
            pass

        url = '/'.join((BASE_URL, 'dir'))
        ret = _get(url)

        all_models = [ m for m in json.loads(ret.text)]
        print "Available models"
        for i, model in enumerate(all_models):
            print "id: %-100s [%s]"%(model['id'],  '\t'.join(["%s: '%s'"%(k, model.get(k, 'N/A')) for k in ("category", "external_id")]))

        logging.debug(pprint.pformat(all_models))

        if not args.dry_run:
            models = list()
            model_ids = list()
            for model in all_models:
                id_ = model['id']
                if len(ids) > 0 and not id_ in ids:
                    # skip if we got ids from cli
                    continue
                models.append(model)
                model_ids.append(id_)
    
            job_ids = submit_jobs(models)
    
            url = '/'.join((BASE_URL, 'jobs'))
            ret = _get(url)
            all_jobs = ret.json()
    
            for job_id in job_ids:
                assert(job_id in all_jobs)
    
            observing_jobs(job_ids, interval=args.poll, duration=args.duration, cancel_after=args.delete)
    
            print_result(zip(job_ids, model_ids) )

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        pass
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + str(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        raise e
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
