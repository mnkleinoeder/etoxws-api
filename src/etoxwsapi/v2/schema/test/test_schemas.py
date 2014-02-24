

import unittest
from etoxwsapi.v2 import schema
import warlock
import copy

##################################################################################################
##################################################################################################
class Test_ws_info(unittest.TestCase):
	def setUp(self):
		self.ws_info = schema.get('ws_info')
	def test_schema(self):
		ws = self.ws_info.create_object(provider="test", admin_email="test@example.com")
		try:
			ws = self.ws_info.create_object(provider="test", admin_email="not_a_valid_email")
			self.assert_(False, "e-mail validation should throw but didn't")
		except ValueError, e:
			pass

##################################################################################################
##################################################################################################
class Test_calculation_info(unittest.TestCase):
	def setUp(self):
		self.calculation_info = schema.get('calculation_info')
	def test_break_id_constraints(self):
		# must fail because model id is not in correct format
		self.assertRaises(ValueError, self.calculation_info.create_object, id="model_name_must_fail")

	def test_comply_id_contraints(self):
		self.calculation_info.create_object(id="/cat/name/1", category="ENDPOINT")

	def test_with_value_spec(self):
		o = self.calculation_info.create_object(id="/cat/name/1", category="ENDPOINT")

		res = schema.get("result_endpoint").schema
		res['properties']['result'] = { "enum": ["positive", "negative", "unknown"]}
		o['return_type_spec'] = res

 		vts = copy.deepcopy(o['return_type_spec'])
 		vt = warlock.model_factory(vts)
 		t = vt()
 		t.cmp_id = ""
 		t.result = "positive"

##################################################################################################
##################################################################################################
class Test_job_status(unittest.TestCase):
	def setUp(self):
		self.job_status = schema.get('job_status')
		
		print self.job_status.schema['properties'].keys()

	def test_must_break(self):
		self.assertRaises(ValueError, self.job_status.create_object, status="JOB_ACCEPTE")
		self.assertRaises(ValueError, self.job_status.create_object, status="job_completed")
	def test_create(self):
		p = self.job_status.create_object()
		p.status = "JOB_UNKNOWN"

class Test_result_metabolism(unittest.TestCase):
	def setUp(self):
		self.result_metabolism = schema.get('result_metabolism')
		self.metabolite = schema.get('metabolite')
	def test_create(self):
		result = [
			self.metabolite.create_object(structure="sdf ...", probability=0.1)
		]
		o = self.result_metabolism.create_object(result=result)

if __name__ == "__main__":
	unittest.main()
	
	
	
	
	