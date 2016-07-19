#-*- coding: utf-8 -*-

import json
import sys
import subprocess
import os
import re
import tempfile

from etoxwsapi.v3 import schema
from etoxwsapi.v3 import wsbase
from .ws_impl_v2 import WS2
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class WS3(WS2):

    def __init__(self):
        self.my_models = list()

        calculation_info = schema.get('calculation_info')

        """
        create calculation info with default value data type (number)
        """
        self.m1_id = '/Sample Path/Sample Model/1'
        self.m1_1 = calculation_info.create_object(id=self.m1_id, category="ENDPOINT", version="1")
        self.m1_1['return_type_spec'] = schema.get("result_endpoint").schema

        self.my_models.append(self.m1_1)

        """
        create calculation info with default value data type (number)
        """
        self.m1_2 = calculation_info.create_object(id=self.m1_id, category="ENDPOINT", version="2")
        self.m1_2['return_type_spec'] = schema.get("result_endpoint").schema

        self.my_models.append(self.m1_2)

        """
        define a categorical return type
        """
        self.m2_id = '/Sample Path/Other Sample Model/1'
        self.m2_1 = calculation_info.create_object(id=self.m2_id, category="ENDPOINT", version="1")
        self.m2_1['license_end'] = -1 #time.mktime(time.strptime("2016 06 30 0 0 0", "%Y %m %d %H %M %S"))
        self.m2_1['license_info'] = "License for software XYZ from company ABC required. Please contact model admin"
        r_type = schema.get("result_endpoint").schema
        r_type['properties']['value'] = { "enum": ["positive", "negative", "unknown"]}
        self.m2_1['return_type_spec'] = r_type

        self.my_models.append(self.m2_1)

    def calculate_impl(self, jobobserver, calc_info, sdf_file):
        def check_lic(ci):
            lic_end = ci.get('license_end', 0)
            if -1 == lic_end:
                raise wsbase.NoValidLicense()
            elif 0 < lic_end:
                if time.time() > lic_end:
                    raise wsbase.LicenseExpired(lic_end)
        for m in self.my_models:
            if m['id'] == calc_info['id']:
                check_lic(m)
        super(WS2, self).calculate_impl(self, jobobserver, calc_info, sdf_file)
