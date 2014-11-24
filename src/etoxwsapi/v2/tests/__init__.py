
import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.testcases import SimpleTestCase
from pprint import pprint, pformat
import json
from etoxwsapi.v2 import schema
import logging

from etoxwsapi.v2.tests.test_infos import *
from etoxwsapi.v2.tests.test_jobs import *

#class Test(SimpleTestCase):
#    def _get_calc_infos(self):
#        resp = self.client.get('/etoxwsapi/v2/dir')
#        self.assertEqual(resp.status_code, 200)
#        data = json.loads(resp.content)
#        return data
#
#    def test_dir(self):
#        calc_infos = self._get_calc_infos()
#        logging.info("Found %d calculation_info(s)"%( len(calc_infos) ) )
#        logging.info( pformat( calc_infos ) )
#        cinfo_schema = schema.get('calculation_info')
#        cinfo_schema.validate(calc_infos[0])
#
#    def submit_jobs(self, models):
#        """
#        preparing request for calculation
#        """
#        calculation_request = schema.get('calculation_request')
#        calculation_info = schema.get('calculation_info')
#
#        req_obj = calculation_request.create_object()
#    
#        req_obj.req_calculations = models
#    
#        fname = os.path.join(THIS_DIR, "tiny.sdf")
#        with open(fname) as fp:
#            req_obj.sdf_file = fp.read()
#    
#        req_ret = requests.post(BASE_URL+"/jobs/", data = req_obj.to_json())
#    
#        if req_ret.status_code == 200:
#            job_ids = list()
#            for stat in json.loads(req_ret.text):
#                job_ids.append(stat['job_id'])
#                print "======================================================================"
#                print "new job submitted."
#                for t in ("job_id", "status"): #, "msg"):
#                    print "%s: %s"%(t, stat[t])
#        else:
#            raise Exception("Failed to submit jobs (%s): %s"%(req_ret.status_code, req_ret.text))
#    
#        return job_ids
#
#    def test_run_ws(self):
#        calc_infos = self._get_calc_infos()
#        

if __name__ == "__main__":
    import django
    django.setup()

    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    unittest.main()
