#-*- coding: utf-8 -*-

import json
import sys
import subprocess
import os
import re
import tempfile
import traceback
import shutil

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
                            "homepage": "http://www.mn-am.com",
                            "admin": "Thomas Kleinoeder",
                            "admin_email": "thomas.kleinoeder@mn-am.com",
        }
        ws = ws_info.create_object(**data)
        return ws.to_json()

    def dir_impl(self):
        return json.dumps(self.my_models)

    def calculate_impl(self, jobobserver, calc_info, sdf_file):
        tmp_dir = None
        try:
            result_endpoint_schema = schema.get("result_endpoint")

            calculation_program = os.path.join(THIS_DIR, 'sample_calculation_program.py')
    
            tmp_dir = tempfile.mkdtemp()
    
            infile = os.path.join(tmp_dir, 'input.sdf')
    
            with open(infile, 'wb') as fp:
                fp.write(sdf_file)
    
            outfile = os.path.join(tmp_dir, "output.tsv")
    
            jobobserver.log_info("calculation for %s (version %s)"%(calc_info['id'], calc_info['version']))
    
            regex = re.compile("\*\*\* RECORD no\.:\s+(\d+)\s+read \*")
    
            cerr_cache_fname = os.path.join(tmp_dir, "cerr_cache")
            cerr_cache = open(cerr_cache_fname, 'w+b')
    
            p = subprocess.Popen([sys.executable, calculation_program, calc_info['id'], calc_info['version'], infile, outfile]
                                                    ,stdout=subprocess.PIPE, stderr=cerr_cache)
    
            jobobserver.report_started(p.pid)

            jobobserver.report_progress(0)
            while True:
                retcode = p.poll() #returns None while subprocess is running
                line = p.stdout.readline()
                #jobobserver.log_info(line)
                if (retcode is not None):
                    break
                else:
                    try:
                        jobobserver.log_debug(line)
                        m = regex.search(line)
                        if m:
                            jobobserver.report_progress(int(m.group(1)))
                    except Exception, e:
                        jobobserver.log_warn("Could not process output from command: %s (%s)"%(line, e))
    
            cerr_cache.seek(0)
            #jobobserver.report_status(retcode, p.stderr.read())
            jobobserver.report_status(retcode, cerr_cache.read())
            cerr_cache.close()
    
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

        except Exception, e:
            jobobserver.report_status(1, str(e))
            jobobserver.log_error(traceback.format_exc().splitlines())
        finally:
            try:
                shutil.rmtree(tmp_dir)
            except Exception, te:
                jobobserver.log_warn("Could not delete tmpdir %s (%s)"%(tmp_dir, te))
      
