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
import traceback

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

def observing_jobs(jobs, interval, duration, cancel_after):
    print "Observing running jobs."
    if duration:
        print "Timeout: %d seconds"%(duration)
    poll = True
    i = 0
    while(poll):
        poll = False
        for job_id,model_id in jobs:
            if i == cancel_after:
                delete_job(job_id)
            url = '/'.join((BASE_URL, "jobs", job_id))
            ret = _get(url)
            stat = ret.json()
            print "status for '%s': %s (%s)"%(job_id, stat['status'], model_id) # stat['currecord'], stat['nrecord'])
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
        parser.add_argument("-C", "--cleanup", action='store_true', dest="do_cleanup", help="tries to delete all existing jobs")
        parser.add_argument("-P", "--print-summary", dest="print_summary", const='stdout', help="print summary and quit", nargs='?', default=None, required=False)
        parser.add_argument("-n", "--dry-run", action='store_true', help="don't trigger calculation")

        # Process arguments
        args = parser.parse_args()

        FORMAT = "%(levelname)s: %(message)s"
        print args.loglev
        logging.basicConfig(level=logging.getLevelName(args.loglev), format=FORMAT)

        DRY_RUN = args.dry_run
        if args.dry_run:
            print ""
            print "-n is deprecated: Use -P to print VM summary."
            print ""

        BASE_URL = args.baseurl
        TEST_FILE = args.testfile

        url = '/'.join((BASE_URL, 'dir'))
        ret = _get(url)

        all_models = [ m for m in json.loads(ret.text)]
        logging.debug(pprint.pformat(all_models))

        if args.do_cleanup:
            url = '/'.join((BASE_URL, 'jobs/'))
            ret = _get(url)
            for job_id in json.loads(ret.text):
                print url+job_id
                requests.delete(url+job_id, verify=SSL_VERIFY)

        elif args.print_summary:
            DRY_RUN = True

            url = '/'.join((BASE_URL, 'info'))
            ret = _get(url)
            info = json.loads(ret.text)

            delim = 160 * '='
            if args.print_summary == 'trac':
                print "=== %s ==="%(info['provider'])
            else:
                print delim
                msg = "Webservice information:"
                print msg
                print '-' * len(msg)

                for k in ('provider', 'homepage', 'admin', 'admin_email'):
                    print "%-12s: %s"%(k, info[k])

            if args.print_summary == 'trac':
                frmt = '|| {{{%-100s}}} ||'
                for model in sorted([ m['id'] for m in all_models]):
                    print frmt%(model)
            else:
                print delim
                frmt = '| %-3s | %-100s | %-9s | %-15s | %-100s |'
                print "Available models:"

                header = frmt%("#", "ID", "version", "category", "external_id")
                print '-' * len(header)
                print header
                print '-' * len(header)
                for i, model in enumerate(all_models):
                    print frmt%(i, model['id'], model.get('version', '1'), model.get('category', 'N/A'), model.get('external_id', 'N/A'))
                print '-' * len(header)
        else:
            #import pydevd; pydevd.settrace()
            ids = list()
            if args.ids:
                for mid in args.ids.split(','):
                    if mid[0] == '/':
                        ids.append(mid)
                    else:
                        try:
                            ids.append(all_models[int(mid)]['id'])
                        except Exception, e:
                            logging.warn("Could not convert index %s"%(e))



            models = list()
            model_ids = list()
            for model in all_models:
                model_id = model['id']
                if ids and not model_id in ids:
                    # not in ids given by -i option
                    continue
                models.append(model)
                model_ids.append(model_id)

            job_ids = submit_jobs(models)

            url = '/'.join((BASE_URL, 'jobs/'))
            ret = _get(url)
            all_jobs = ret.json()

            for job_id in job_ids:
                assert(job_id in all_jobs)

            observing_jobs(zip(job_ids, model_ids), interval=args.poll, duration=args.duration, cancel_after=args.delete)

            print_result(zip(job_ids, model_ids))

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        pass
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + str(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        sys.stderr.write(traceback.format_exc())
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
