import os
from django.core.urlresolvers import reverse
from django.test import TestCase
from .. import schema, jobs
import types

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class JobsTest(TestCase):
	def _submit_job(self):
		calculation_info = schema.get('calculation_info')
		calculation_request = schema.get('calculation_request')

		url = reverse("v2_dir")
		response = self.client.get(url)

		models = calculation_info.loads(response.content)
		self.assertIsInstance(models, types.ListType)

		"""
		preparing request for calculation
		"""
		req_obj = calculation_request.create_object()

		req_obj.req_calculations = models

		fname = os.path.join(THIS_DIR, "tiny.sdf")
		with open(fname) as fp:
			req_obj.sdf_file = fp.read()

		url = reverse("jobs")
		response = self.client.post(url, content_type = 'application/json', data=req_obj.to_json())
		print "new job submitted. job_id is: %s"%(response.content)
		

# 	def setUp(self):
# 		self._submit_job()
	def test_submit_job(self):
		self._submit_job()
		
