
from django.core.urlresolvers import reverse
from django.test import TestCase
from etoxwsapi.v3 import schema
import logging
import unittest
import json
from jinja2.utils import pformat

class MetaInfoTest(TestCase):
    def _get_response(self, view_name):
        url = reverse(view_name)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        return response

    def test_info(self):
        try:
            response = self._get_response("v3_info")
            ws_info = schema.get('ws_info')
            ws_info.loads(response.content)
        except ValueError, e:
            self.fail("Could not validate object:\n%s"%(e))

    def test_dir(self):
        try:
            calc_info_schema = schema.get('calculation_info')

            response = self._get_response("v3_dir")
            calc_infos = json.loads(response.content)
            logging.info("Found %d calculation_info(s)"%( len(calc_infos) ) )
            logging.info( pformat( calc_infos ) )
            for ci in calc_infos:
                calc_info_schema.validate(ci)

        except ValueError, e:
            self.fail("Could not validate object:\n%s"%(e))

if __name__ == "__main__":
    import django
    django.setup()

    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    unittest.main()
