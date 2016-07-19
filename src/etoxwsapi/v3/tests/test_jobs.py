import os
from django.core.urlresolvers import reverse
from django.test import TestCase
from etoxwsapi.v3 import schema
from etoxwsapi.v3 import jobs_v3
import types
import logging
import unittest
from pprint import pformat, pprint
import json
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

###########################################################################
#
# This test does not work anymore because of the usage of the celery
# job manager
#
###########################################################################

class JobsTest(TestCase):
    def _submit_job(self):
        calculation_info_schema = schema.get('calculation_info')
        calculation_request_schema = schema.get('calculation_request')

        url = reverse("v3_dir")
        response = self.client.get(url)

        models = calculation_info_schema.loads(response.content)
        self.assertIsInstance(models, types.ListType)

        """
        preparing request for calculation
        """
        req_obj = calculation_request_schema.create_object()

        req_obj.req_calculations = models

        fname = os.path.join(THIS_DIR, "tiny.sdf")
        with open(fname) as fp:
            req_obj.sdf_file = fp.read()

        url = reverse("jobs_v3")
        response = self.client.post(url, content_type = 'application/json', data=req_obj.to_json())
        return response

    def test_submit_job(self):
        job_status_schema = schema.get('job_status')
        response = self._submit_job()
        logging.info("new jobs_v3 submitted.")
        
        jobs_v3 = json.loads(response.content)

        logging.info("Submitted job ids:")
        for job in jobs_v3:
            job_status_schema.validate(job)
            logging.info(job['job_id'])

        url = reverse("jobs_v3")

        poll = True
        while(poll):
            time.sleep(1)
            poll = False
            for job in jobs_v3:
                jobid = job['job_id']
                u = url+"/jobs_v3/%s"%(jobid)
                response = self.client.get(u)
                self.assertEqual(200, response.status_code)
                if response.status_code == 200:
                    job_status = json.loads(response.content)
                    if job_status['status'] != "JOB_SUCCESS":
                        poll = True
                    pprint(job_status)

if __name__ == "__main__":
    import django
    django.setup()

    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT, )
    unittest.main()
