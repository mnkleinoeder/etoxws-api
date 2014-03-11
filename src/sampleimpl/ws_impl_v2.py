#-*- coding: utf-8 -*-

import json
import sys
import subprocess
import os
import re
import tempfile
import logging

from etoxwsapi.v2 import schema
from etoxwsapi.v2.wsbase import WebserviceImplementationBase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class WS2(WebserviceImplementationBase):

	def __init__(self):
		self.my_models = list()

		calculation_info = schema.get('calculation_info')

		"""
		create calculation info with default value data type (number)
		"""
		self.ames_id = '/Tox/Genotox/Mutagen/AMES/1'
		self.ames_1 = calculation_info.create_object(id=self.ames_id, category="ENDPOINT", external_id = "eTOXvault ID1")
		self.ames_1['return_type_spec'] = schema.get("result_endpoint").schema

		self.my_models.append(self.ames_1)

		"""
		define a categorical return type
		"""
		self.dipl_id = '/Tox/Organ Tox/Phospholipidosis/DIPL/1'
		self.dipl_1 = calculation_info.create_object(id=self.dipl_id, category="ENDPOINT", external_id = "eTOXvault ID2")
		r_type = schema.get("result_endpoint").schema
		r_type['properties']['value'] = { "enum": ["positive", "negative", "unknown"]}
		self.dipl_1['return_type_spec'] = r_type

		self.my_models.append(self.dipl_1)

	def info_impl(self):
		ws_info = schema.get('ws_info')
		data = { "provider": "Molecular Networks GmbH",
							"homepage": "http://www.molecular-networks.com",
							"admin": "Thomas Kleinoeder",
							"admin_email": "kleinoeder@molecular-networks.com",
		}
		ws = ws_info.create_object(**data)
		return ws.to_json()

	def dir_impl(self):
		return json.dumps(self.my_models)

	def calculate_impl(self, jobobserver, calc_info, sdf_file):
		calculation_program = os.path.join(THIS_DIR, 'sample_calculation_program.py')

		infile = tempfile.mktemp(suffix=".sdf")
		with open(infile, "wb") as fp:
			fp.write(sdf_file)

		outfile = tempfile.mktemp(suffix=".sdf")

		logging.info("calculation for %s"%(calc_info['id']))

		regex = re.compile("\*\*\* RECORD no\.:\s+(\d+)\s+read \*")

		p = subprocess.Popen([sys.executable, calculation_program, calc_info['id'], infile, outfile]
												,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		while True:
			retcode = p.poll() #returns None while subprocess is running
			line = p.stdout.readline()
			if (retcode is not None):
				break
			else:
				m = regex.search(line)
				if m:
					jobobserver.report_progress(int(m.group(1)))

		jobobserver.report_status(retcode, p.stderr.read())
		if retcode == 0:
			with open(outfile) as fp:
				for i, line in enumerate(fp):
					r = line.strip().split('\t')
					result = dict()
					result['cmp_id'] = i
					result['value'] = r[0]
					result['success'] = True
					result['AD'] = { "value": r[1], "success": True, "message": "" }
					result['RI'] = { "value": r[2], "success": True, "message": "" }
					jobobserver.report_result(i, json.dumps(result))


