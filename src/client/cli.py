# encoding: utf-8

#import pydevd; pydevd.settrace()

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
import glob

from blessings import Terminal
import signal

from etoxwsapi.utils import SDFFile
from etoxwsapi.v2 import schema
from etoxwsapi.v2 import utils as v2_utils
from etoxwsapi.v2.utils import SSL_VERIFY, JobStat, http_get, extract_val

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(THIS_DIR, ".."))

## defaults
_INFILE = os.path.join(THIS_DIR, "tiny.sdf")
_BASE_URL = 'http://localhost:8000/etoxwsapi/v2'
_LOG_LEV = "WARN"

term = Terminal()

class TermMixin():
    delim1 = "="*101
    delim2 = "-"*100

    def _print(self, t, msg = ""):
        prfx = '| '

        if msg == self.delim1:
            prfx = '|'

        if self.use_term:
            print t + prfx + msg
        else:
            print prfx + msg

        
class CalculationTask(object, TermMixin):
    def __init__(self, handler, sdf_fname, term_pos):
        self.handler = handler
        self.use_term = handler.use_term
        self.wsinfo = handler.wsinfo
        self.baseurl = handler.baseurl
        self.models = handler.get_selected_models()
        self.fname = sdf_fname
        self.sdf_file = SDFFile(sdf_fname)
        self.term_pos = self.term_pos_initial = term_pos
        self.jobs = None
        
        super(CalculationTask, self).__init__()


    def run(self):
        self._submit()
        self._poll()
        self._analyze_results()

    def write(self, fname):
        self.sdf_file.write(fname)

    def kill(self):
        for job in self.jobs:
            requests.delete(self.baseurl + '/jobs/' + job.job_id, verify=SSL_VERIFY)

    def success(self):
        return ( len([j for j in self.jobs if j.success()]) == len(self.jobs) )

    def _submit(self):
        self.jobs = v2_utils.submit_jobs(self.wsinfo['provider'], self.baseurl, self.models, self.sdf_file.to_string(ctab_only=True))

    def _poll(self):
        interval = 1
        while(True):
            do_poll = False
            running = []
            naccepted = 0

            v2_utils.update_jobs(self.jobs)

            for job in self.jobs:
                logging.debug(job.stat)
                #print "status for '%s': %s (%s), %s/%s"%(job_id, stat['status'], model_id, stat['currecord'], stat['nrecord'])
                if job.stat['status'] == "JOB_RUNNING":
                    running.append(job)
                elif job.stat['status'] == "JOB_ACCEPTED":
                    naccepted += 1

                if job.stat['status'] not in ( "JOB_COMPLETED", "JOB_FAILED", "JOB_REJECTED", "JOB_CANCELLED"):
                    do_poll = True

                time.sleep(interval)

            if not do_poll:
                break

            self._print( term.clear_eos(self.term_pos) )
            if running:
                for i, job in enumerate(running):
                    self._print( term.move(self.term_pos+i)+term.clear_eol(),
                                 term.yellow(term.blink("Running: "))
                                 + job.model_id + " (%s/%s)"%(job.stat['currecord'], job.stat['nrecord']) ) 
            elif naccepted:
                self._print(term.move(self.term_pos), "Waiting for job execution. %s job(s) accepted"%(naccepted))
            else:
                self._print(term.move(self.term_pos), "No job accecpted yet. Is the job queue (celery) running? Please check.")

    def _analyze_results(self):
        v2_utils.analyze_job_results(self.jobs, self.sdf_file)

    def print_results(self, outstr = sys.stdout):
        frmt = '| %-7s | %-20s | %-20s | %-20s |'
        for job in self.jobs:
            print >>outstr, ""
            print >>outstr, "Model '%s' (job: %s)\n"%(job.model_id, job.job_id)
            results = job.stat.get('results', None)
            if results:
                print >>outstr, '-' * len(frmt%('','','',''))
                print >>outstr, frmt%("cmp_id", "value", "AD", "RI")
                print >>outstr, '-' * len(frmt%('','','',''))
                for r in results:
                    line = frmt%( r['cmp_id'], extract_val(r, 'value', None), extract_val(r, 'AD','value'), extract_val(r, 'RI','value') )
                    if r.get('message', None):
                        print >>outstr, line, r['message']
                    else:
                        print >>outstr, line
                print >>outstr, '-' * len(frmt%('','','',''))
            else:
                print >>outstr, "No results available"
                print '\n'.join([m for lev, m in job.summary if lev == JobStat.CRIT])

class WSClientHandler(object, TermMixin):
    def __init__(self, prog, args):
        self.prog = prog
        self.args = args
        self.use_term = (not self.args.verbose)
        
        self.calc_tasks = []
        
        self.baseurl = self.args.baseurl

        url = '/'.join((self.args.baseurl, 'info'))
        ret = http_get(url)
        self.wsinfo = schema.validate(json.loads(ret.text), schema.get('ws_info'))

        url = '/'.join((self.args.baseurl, 'dir'))
        ret = http_get(url)
        #self.models = [ m for m in json.loads(ret.text)]
        self.models = [ schema.validate(m, schema.get('calculation_info')) for m in json.loads(ret.text)
                                if m['id'] != "/Toxicity/Target Safety Pharmacology/Hyperbilirubinemia/1"]

        logging.debug(pprint.pformat(self.wsinfo))
        logging.debug(pprint.pformat(self.models))

        self.current_jobs = None
        self.cur_line = 0

        super(WSClientHandler, self).__init__()

    def _create_task(self, fname, term_pos):
        c = CalculationTask(self, fname, term_pos)
        self.calc_tasks.append(c)
        return c

    def get_selected_models(self):
        models = list()

        req_ids = list()
        if self.args.ids:
            ids = set()
            
            for t in self.args.ids.split(','):
                cur = set()
                r = t.split('-')
                if len(r) == 1:
                    cur.add(int(r[0]))
                elif len(r) == 2:
                    cur.update(range(int(r[0]), int(r[1])+1))
                ids.update(cur)
            for i in ids:
                if i < 0 or i >= len(self.models):
                    raise IndexError("Requested model with index '%d' is out of range"%(i))
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

    def inspect_jobs(self):
        ret = http_get('/'.join((self.args.baseurl, 'jobs/')))
        for job_id in json.loads(ret.text):
            print job_id
            url = '/'.join((self.baseurl, "jobs", job_id))
            ret = http_get(url)
            stat = ret.json()
            print stat

    def kill_running_jobs(self):
        for task in self.calc_tasks:
            task.kill()

    def calc(self):
        self._print( term.clear() )
        self._print( term.move(0, 0), "Calculation for '%s' ... in progress."%(self.args.infile))
        self._print( term.move(1, 0), "Waiting for job executions ..." )
        c = self._create_task(self.args.infile, 1)
        c.run()
        c.write(self.args.outfile)
        self._print( term.move(1, 0)+term.clear_eos(), "Calculation for '%s' ... %s"%(self.args.infile, term.green(" Completed"))) 
        self._print( term.move(2, 0)+term.clear_eos(), "Results written to '%s'."%(self.args.outfile)) 

    def _run_test(self, testfile, term_pos):
        self._print( term.move(term_pos, 0), "Testing: %s ... in progress."%(testfile))
        self._print( term.move(term_pos+1, 0), "Waiting for job executions ..." )
        c = self._create_task(testfile, term_pos+1)
        c.run()
        self._print( term.move(term_pos, 0)+term.clear_eos(), "Testing: %s ... %s"%(testfile, term.green(" Completed"))) 

    def _write_summary(self):

        for c in self.calc_tasks:
            self._print("", self.delim1)
            self._print("",  "Testing results for '%s'"%(c.fname) )
            for job in c.jobs:
                self._print("", self.delim2)
                if job.success():
                    stat = term.green("Okay")
                else:
                    stat = term.red("FAILED")
                self._print("", "[Model %s]: %s"%(job.model_id, stat))
                #self._print("", "-"*80)
                for s1, t, m in ((JobStat.CRIT, term.red, "|- Critical errors:"), (JobStat.WARN, term.yellow, "|- Warnings"), (JobStat.INFO, term.normal, "|- Information messages")):
                    if job.nmessage(s1):
                        self._print("", m)
                        for s2, m in job.summary:
                            if s1 == s2:
                                self._print("", t(m))
            self._print("", self.delim1)
            self._print("","")

    def _write_results(self):
        self._print("", self.delim1)
        self._print("", "*** Dumping raw results as received from webservice ***")
        for c in self.calc_tasks:
            self._print("", "")
            self._print("", self.delim1)
            self._print("",  "Results for '%s'"%(c.fname) )
            self._print("", self.delim1)
            self._print("", "")
            c.print_results()
        
    def test(self):
        self._print( term.clear() )
        self._print( term.move(0), "==> Running tests for %s <=="%(self.args.baseurl) )
        self._run_test(self.args.infile, 1)
        self._write_results()
        self._print( "", "==> Done for %s <=="%(self.args.baseurl) )
        
    def test_long(self):
        
        if self.args.infile:
            testfiles = self.args.infile.split(',')
        else:
            testdir = os.path.join(THIS_DIR, 'testdata')
            testfiles = glob.glob(os.path.join(testdir, '*.sdf'))
            testfiles.extend(glob.glob(os.path.join(testdir, '*.mol')))

        #testfiles = [ os.path.join(THIS_DIR, 'testdata', 'utf-8.sdf') ]

        self.cur_line = 0
        self._print( term.clear() )
        self._print( term.move(self.cur_line, 0), "==> Running tests for %s <=="%(self.args.baseurl) )
        for i, testfile in enumerate(testfiles):
            #if 'huge' in testfile:
            #    continue
            self.cur_line = i+1
            self._run_test(testfile, self.cur_line)
        #self.cur_line = i+1
        self._write_summary()
        if self.args.print_results:
            self._write_results()
        self._print("", "")
        self._print("", self.delim1)
        self._print("", "Test summary per test file:")
        self._print("", self.delim2)
        model_summary = {}
        for c in self.calc_tasks:
            frmt = '%-81s: %-19s '
            if c.success():
                status = term.green("All tests passed")
            else:
                status = term.red("Tests failed.")
            self._print("", frmt%(c.fname, status))
            for job in c.jobs:
                if not job.success():
                    model_summary.setdefault(job.model_id, []).append(c.fname)
        self._print("", self.delim1)
        self._print("", "")
        self._print("", self.delim1)
        self._print("", "Prediction failures observed for files:")
        self._print("", self.delim2)
        no_failures = True
        for m, ff in model_summary.iteritems():
            no_failures = False
            self._print("", "[%s]"%(m))
            for f in ff:
                self._print("", " - %s"%(f))
        if no_failures:
            self._print("", "No failures!")
        self._print("", self.delim1)
        #print term.move(self.cur_line,0) + "All tests done.                                                              "

    def dir_info(self):
        if self.args.print_summary == 'trac':
            print "=== %s ==="%(self.wsinfo['provider'])
        else:
            print self.delim1
            msg = "Webservice information:"
            print msg
            print self.delim2

            for k in ('provider', 'homepage', 'admin', 'admin_email'):
                print "%-20s: %s"%(k, self.wsinfo[k])
            print "%-20s: %s"%("Number of models", len(self.models) )

        if self.args.print_summary == 'trac':
            frmt = '|| {{{%-100s}}} ||'
            for model in sorted([ m['id'] for m in self.models]):
                print frmt%(model)
        else:
            print self.delim1
            frmt = '| %-3s | %-100s | %-9s | %-15s | %-100s |'
            print "Available models:"

            header = frmt%("#", "ID", "version", "category", "external_id")
            print '-'*len(header)
            print header
            print '-'*len(header)
            for i, model in enumerate(self.models):
                print frmt%(i, model['id'], model.get('version', '1'), model.get('category', 'N/A'), model.get('external_id', 'N/A'))
            print '-'*len(header)

    def check_etoxvault(self):
        ret = requests.get('http://phi.imim.es/allmodels/?authkey=%s'%(self.args.authkey))
        
        if (ret.status_code != 200):
            raise Exception("Could not retrieve data from eTOXvault (HTTP: %s)"%(ret.status_code))

        all_recs = []        
        for rec in ret.json():
            mtag, mid = v2_utils.modelid(rec['modeltag'], rec['partner'], rec['version'])
            print mtag
            all_recs.append(mid)
        frmt = '%-81s: %-19s '
        for m in self.get_selected_models():
            #pprint.pprint(m)
            mtag, mid = v2_utils.modelid_from_calcinfo(self.wsinfo['provider'], m)
            if mid in all_recs:
                status = term.green("Available.")
            else:
                status = term.red("Missing!")
            self._print("", frmt%(mtag, status))
            
        

class CLI(object):
    def __init__(self):
        pass
    def run(self):
        # Setup argument parser
        parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description="""
            Command line interface to access the eTOX webservices (based on API v2.1)
            running calculation can be stopped anytime by Ctrl-C.""",
        )

        i_option = (("-i", "--ids"), {'dest': "ids", 'help': "comma-separated list with IDs to be calculated [default: all, as obtained by /dir]", 'default':None})
        parser.add_argument("-b", "--base-url", dest="baseurl", help="base url of webservice to be tested [default: %(default)s]", default=_BASE_URL)
        parser.add_argument("-l", "--log-level", dest="loglev", help="set verbosity level [default: %(default)s] (see python logging module)", default=_LOG_LEV)
        parser.add_argument("-v", "--verbose", dest="verbose", help="write output sequentially to the terminal", default=False, action='store_true')

        subparsers = parser.add_subparsers(help='available subcommands')

        parser_test = subparsers.add_parser('test', help="""run models with a tiny dataset of three simple molecules (testdata/tiny.sdf).
                                                                   This is useful only while developing and debugging.""")
        parser_test.add_argument("-t", "--test-file", dest="infile", help="SDFile to be used for the test run. [default: %(default)s]", default=_INFILE )
        parser_test.add_argument(*i_option[0], **i_option[1])
        parser_test.set_defaults(func='test')

        parser_test2 = subparsers.add_parser('test-long', help="""run models with an extensive test-suite (i.e., all sdf-files in testdata/ subdir).
                                                                 This test must pass before a VM is accepted for deployment.""")
        parser_test2.add_argument(*i_option[0], **i_option[1])
        parser_test2.add_argument("-P", "--print-results", dest="print_results", help="print results to terminal", default=False, action='store_true')
        parser_test2.add_argument("-t", "--test-file", dest="infile", default=None, help="""comma separated list of SDFiles to be used for the test run.
                                    If not specified all files found in the testdata/ subdir will be used""")
        parser_test2.set_defaults(func='test_long')

        parser_calc = subparsers.add_parser('calc', help='calculation help')
        parser_calc.set_defaults(func='calc')
        parser_calc.add_argument("-I", "--input-file", dest="infile", help="SDFile to be used as input file for calculations.", required=True )
        parser_calc.add_argument("-O", "--output-file", dest="outfile", help="SDFile to be used as output file.", required=True )
        parser_calc.add_argument(*i_option[0], **i_option[1])

        parser_jobs = subparsers.add_parser('inspect-jobs', help='inspect jobs')
        parser_jobs.set_defaults(func='inspect_jobs')

        parser_evault = subparsers.add_parser('etoxvault-check', help='check if a eTOXvault record is available for all models')
        parser_evault.set_defaults(func='check_etoxvault')
        parser_evault.add_argument("-k", "--authkey", dest="authkey", help="Access key for eTOXvault REST API.", required=True )
        parser_evault.add_argument(*i_option[0], **i_option[1])

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

        class exit_gracefully:
            def __init__(self, handler):
                self.handler = handler
            def __call__(self, signum, frame):
                self.handler._print( term.clear(), "Test run interrupted by user request. Cleaning up jobs ...")
                self.handler.kill_running_jobs()
                sys.exit()

        signal.signal(signal.SIGINT, exit_gracefully(handler))

        return handler.dispatch(args.func)

if __name__ == '__main__':
    cli = CLI()
    sys.exit(cli.run())
