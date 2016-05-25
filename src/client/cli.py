# encoding: utf-8

import sys
import os
import requests
import time
import json
import pprint
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import traceback

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(THIS_DIR, ".."))

from etoxwsapi.v2 import schema

SSL_VERIFY=False

## defaults
_INFILE = os.path.join(THIS_DIR, 'testdata', "tiny.sdf")
_BASE_URL = 'http://localhost:8000/etoxwsapi/v2'
_LOG_LEV = "WARN"
_POLL_INTERVALL = 5
_DURATION = -1
_DELETE_AFTER = -1

def http_get(url):
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
        return 'n/a'
    except Exception, e:
        print type(e)
        raise e

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

class WSClientHandler(object):
    def __init__(self, prog, args):
        self.prog = prog
        self.args = args

        url = '/'.join((self.args.baseurl, 'info'))
        ret = http_get(url)
        self.wsinfo = json.loads(ret.text)
        logging.debug(pprint.pformat(self.wsinfo))

        url = '/'.join((self.args.baseurl, 'dir'))
        ret = http_get(url)
        self.models = [ m for m in json.loads(ret.text)]
        logging.debug(pprint.pformat(self.models))

    def _print_result(self, jobs):
        frmt = '| %-7s | %-10s | %-10s | %-10s |'
        for (job_id,model_id) in jobs:
            print "==========================================================================="
            print "Results for model '%s' (job: %s)\n"%(model_id, job_id)
            ret = http_get('/'.join((self.args.baseurl, 'jobs', job_id)))
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

    def _submit_jobs(self, models):
        """
        preparing request for calculation
        """
        calculation_request = schema.get('calculation_request')
        req_obj = calculation_request.create_object()

        req_obj.req_calculations = models

        with open(self.args.infile) as fp:
            req_obj.sdf_file = fp.read()

        req_ret = requests.post(self.args.baseurl+"/jobs/", data = req_obj.to_json(), verify=SSL_VERIFY,
                                headers={'Content-type': 'application/json'})

        if req_ret.status_code == 200:
            job_ids = list()
            for i, stat in enumerate(json.loads(req_ret.text)):
                job_ids.append( (stat['job_id'], "%s (version %s)"%(models[i]['id'], models[i].get('version', '1'))) )
                print "======================================================================"
                print "new job submitted."
                for t in ("job_id", "status"): #, "msg"):
                    print "%s: %s"%(t, stat[t])
        else:
            raise Exception("Failed to submit jobs (%s): %s"%(req_ret.status_code, req_ret.text))

#            model_ids.append("%s (version %s)"%(model['id'], model['version']))

        return job_ids

    def _delete_job(self, job_id):
        ret = requests.delete(self.args.baseurl + '/jobs/' + job_id, verify=SSL_VERIFY)
        #print ret.status_code, ret.text

    def _observing_jobs(self, jobs, interval=_POLL_INTERVALL, duration=_DURATION, cancel_after=_DELETE_AFTER):
        print "Observing running jobs."
        if duration:
            print "Timeout: %d seconds"%(duration)
        poll = True
        i = 0
        while(poll):
            poll = False
            for job_id,model_id in jobs:
                if i == cancel_after:
                    self._delete_job(job_id)
                url = '/'.join((self.args.baseurl, "jobs", job_id))
                ret = http_get(url)
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


    def _get_selected_models(self):
        models = list()

        req_ids = list()
        if self.args.ids:
            for i in [ int(i) for i in self.args.ids.split(',') ]:
                if i < 0 or i >= len(self.models):
                    raise IndexError("Requested model with index is out of range")
                req_ids.append( i )
        for i, model in enumerate(self.models):
            if req_ids and not ( i in req_ids ):
                continue
            models.append(model)
        return models

    def dispatch(self, func_name):
        try:
            f = getattr(self, func_name)
            f()
        except KeyboardInterrupt, ki:
            ### handle keyboard interrupt ###
            print ki
            print ""
        except Exception, e:
            indent = len(self.prog) * " "
            sys.stderr.write(self.prog + ": " + str(e) + "\n")
            sys.stderr.write(indent + "  for help use --help\n")
            sys.stderr.write(traceback.format_exc())
            return 1
        return 0

    def cleanup(self):
        url = '/'.join((self.args.baseurl, 'jobs/'))
        ret = http_get(url)
        for job_id in json.loads(ret.text):
            print url+job_id
            requests.delete(url+job_id, verify=SSL_VERIFY)

    def _make_prop_entry(self, model, meta, val):
        mid = model['id']
        label, n = mid.split('/')[-2:]
        return ">  <%s #%s (%s, version %s)%s>\n%s\n\n"%(label, n, self.wsinfo['provider'], model.get('version', '1'), meta, val)

        #return ">  <%s v%s (%s)%s>\n%s\n\n"%(mid, model.get('version', '1'), self.wsinfo['provider'], meta, val)

    def calc(self):
        models = self._get_selected_models()
        jobs   = self._submit_jobs(models)
        self._observing_jobs(jobs)

        infp = open(self.args.infile, 'rU')
        outfp = open(self.args.outfile, 'w')

        outrecs = list()
        for sdfrec in infp.read().split('$$$$\n')[:-1]:
            rec = sdfrec.rstrip() + '\n\n'
            outrecs.append( rec )

        for i, (job_id,model_id) in enumerate(jobs):
            ret = http_get('/'.join((self.args.baseurl, 'jobs', job_id)))
            if ret.status_code == 200:
                data = json.loads(ret.text)
                if data['status'] == "JOB_COMPLETED":
                    results = data['results']
                    for r in results:
                        icmp = int(r['cmp_id'])
                        outrecs[icmp] += self._make_prop_entry(models[i], "", _val(r, 'value'))
                        outrecs[icmp] += self._make_prop_entry(models[i], ":ADAN", _val(r, 'AD','value'))
                        outrecs[icmp] += self._make_prop_entry(models[i], ":RI", _val(r, 'RI','value'))
                else:
                    print "Job is not (yet) available: %s (%s)"%(results['status'], results['msg'])
            else:
                print "Could not get job results: %s, %s"%(ret.status_code, ret.text)
        for rec in outrecs:
            print >>outfp, rec+'$$$$'

    def test(self):
        #import pydevd; pydevd.settrace()

        models = self._get_selected_models()
        jobs   = self._submit_jobs(models)

        # test for consistency of job ids
        url = '/'.join((self.args.baseurl, 'jobs/'))
        ret = http_get(url)
        all_jobs = ret.json()
        for job_id,_ in jobs:
            assert(job_id in all_jobs)

        self._observing_jobs(jobs, interval=self.args.poll, duration=self.args.duration, cancel_after=self.args.delete)
        self._print_result(jobs)

    def dir_info(self):
        delim = 160 * '='
        if self.args.print_summary == 'trac':
            print "=== %s ==="%(self.wsinfo['provider'])
        else:
            print delim
            msg = "Webservice information:"
            print msg
            print '-' * len(msg)

            for k in ('provider', 'homepage', 'admin', 'admin_email'):
                print "%-12s: %s"%(k, self.wsinfo[k])

        if self.args.print_summary == 'trac':
            frmt = '|| {{{%-100s}}} ||'
            for model in sorted([ m['id'] for m in self.models]):
                print frmt%(model)
        else:
            print delim
            frmt = '| %-3s | %-100s | %-9s | %-15s | %-100s |'
            print "Available models:"

            header = frmt%("#", "ID", "version", "category", "external_id")
            print '-' * len(header)
            print header
            print '-' * len(header)
            for i, model in enumerate(self.models):
                print frmt%(i, model['id'], model.get('version', '1'), model.get('category', 'N/A'), model.get('external_id', 'N/A'))
            print '-' * len(header)

class CLI(object):
    def __init__(self):
        pass
    def run(self):
        # Setup argument parser
        parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description='Command line interface to access the eTOX webservices (based on API v2)',
        )

        parser.add_argument("-b", "--base-url", dest="baseurl", help="base url of webservice to be tested [default: %(default)s]", default=_BASE_URL)
        parser.add_argument("-l", "--log-level", dest="loglev", help="set verbosity level [default: %(default)s] (see python logging module)", default=_LOG_LEV)

        subparsers = parser.add_subparsers(help='available subcommands')

        parser_test = subparsers.add_parser('test', help='test help')
        parser_test.add_argument("-p", "--poll-interval", dest="poll", type=int, help="poll status each N sec [default: %(default)s]", metavar="N", default= _POLL_INTERVALL)
        parser_test.add_argument("-d", "--duration", dest="duration", type=int, help="stop this program after N sec [default: %(default)s]", metavar="N", default= _DURATION)
        parser_test.add_argument("-c", "--delete-after", dest="delete", type=int, help="issue a DELETE request after N polls [default: %(default)s]", metavar="N", default= _DELETE_AFTER)

        parser_test.add_argument("-t", "--test-file", dest="infile", help="SDFile to be used for the test run. [default: %(default)s]", default=_INFILE )
        parser_test.add_argument("-i", "--ids", dest="ids", help="comma-separated list with IDs to be calculated [default: all, as obtained by /dir]", default=None)

        parser_test.set_defaults(func='test')

        parser_calc = subparsers.add_parser('calc', help='calculation help')
        parser_calc.set_defaults(func='calc')
        parser_calc.add_argument("-I", "--input-file", dest="infile", help="SDFile to be used as input file for calculations.", required=True )
        parser_calc.add_argument("-O", "--output-file", dest="outfile", help="SDFile to be used as output file.", required=True )
        parser_calc.add_argument("-i", "--ids", dest="ids", help="comma-separated list with IDs to be calculated [default: all, as obtained by /dir]", default=None)

        parser_dir = subparsers.add_parser('info', help='prints info and dir from webservice implementation running at base url')
        parser_dir.add_argument("-P", "--print-summary", dest="print_summary", const='stdout', help="output format", nargs='?', default=None, required=False)
        parser_dir.set_defaults(func='dir_info')

        parser_dir = subparsers.add_parser('cleanup', help='cancels and deletes jobs')
        parser_dir.set_defaults(func='cleanup')

        args = parser.parse_args()
        #print args

        FORMAT = "%(levelname)s: %(message)s"
        logging.basicConfig(level=logging.getLevelName(args.loglev), format=FORMAT)


        handler = WSClientHandler(parser.prog, args)

        return handler.dispatch(args.func)

if __name__ == '__main__':
    cli = CLI()
    sys.exit(cli.run())
