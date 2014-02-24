
from django.core.urlresolvers import reverse
from django.test import TestCase
from etoxwsapi.v2 import schema


class MetaInfoTest(TestCase):
	def _get_response(self, view_name):
		url = reverse(view_name)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		return response
	def test_info(self):
		try:
			response = self._get_response("v2_info")
			ws_info = schema.get('ws_info')
			ws_info.loads(response.content)
		except ValueError,e:
			self.fail("ws_info violates schema")

	def test_dir(self):
		try:
			response = self._get_response("v2_dir")
		except Exception, e:
			pass
