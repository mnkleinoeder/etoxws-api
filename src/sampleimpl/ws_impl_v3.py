#-*- coding: utf-8 -*-

import json
import sys
import subprocess
import os
import re
import tempfile

from etoxwsapi.v3 import schema
from etoxwsapi.v3.wsbase import WebserviceImplementationBase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class WS2(WebserviceImplementationBase):

    def __init__(self):
        self.my_models = list()

        calculation_info = schema.get('calculation_info')

        """
        create calculation info with default value data type (number)
        """
        self.ames1_id = '/Tox/Genotox/Mutagen/AMES/1'
        self.ames1_1 = calculation_info.create_object(id=self.ames1_id, category="ENDPOINT", version="1")
        self.ames1_1['return_type_spec'] = schema.get("result_endpoint").schema

        self.my_models.append(self.ames1_1)

        """
        create calculation info with default value data type (number)
        """
        self.ames1_2 = calculation_info.create_object(id=self.ames1_id, category="ENDPOINT", version="2")
        self.ames1_2['return_type_spec'] = schema.get("result_endpoint").schema

        self.my_models.append(self.ames1_2)

        """
        define a categorical return type
        """
        self.dipl_id = '/Tox/Organ Tox/Phospholipidosis/DIPL/1'
        self.dipl_1 = calculation_info.create_object(id=self.dipl_id, category="ENDPOINT", version="1")
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
        result_endpoint_schema = schema.get("result_endpoint")
        calculation_program = os.path.join(THIS_DIR, 'sample_calculation_program.py')

        infile = tempfile.mktemp(suffix=".sdf")
        with open(infile, "wb") as fp:
            fp.write(sdf_file)

        outfile = tempfile.mktemp(suffix=".sdf")

        jobobserver.log_info("calculation for %s (version %s)"%(calc_info['id'], calc_info['version']))

        regex = re.compile("\*\*\* RECORD no\.:\s+(\d+)\s+read \*")

        #
        # check the version
        #

        p = subprocess.Popen([sys.executable, calculation_program, calc_info['id'], calc_info['version'], infile, outfile]
                                                ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        jobobserver.report_started(p.pid)
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
                    result = result_endpoint_schema.create_object()
                    result['cmp_id'] = str(i)
                    result['value'] = float(r[0])
                    result['success'] = True
                    result['AD'] = { "value": float(r[1]), "success": True, "message": "" }
                    result['RI'] = { "value": float(r[2]), "success": True, "message": "" }
                    jobobserver.report_result(i, json.dumps(result))


