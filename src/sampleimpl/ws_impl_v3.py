#-*- coding: utf-8 -*-

import os

from etoxwsapi.v3 import schema
from .ws_impl_v2 import WS2
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class WS3(WS2):
    """
    For simplicity we just redefine the model definitions in __init__ and reuse the
    rest of the code from WS2.
    Please note the license management for the third sample model.
    """
    def __init__(self):
        self.my_models = list()

        calculation_info = schema.get('calculation_info')

        """
        create calculation info with default value data type (number)
        """
        self.m1_id = '/Sample Path/Sample Model/1'
        self.m1_1 = calculation_info.create_object(id=self.m1_id, category="ENDPOINT", version="1")
        self.m1_1['return_type_spec'] = schema.get("result_endpoint").schema
        #self.m1_1['license_end'] = time.mktime(time.strptime("2016 06 30 0 0 0", "%Y %m %d %H %M %S"))

        self.my_models.append(self.m1_1)

        """
        create calculation info with default value data type (number)
        """
        self.m1_2 = calculation_info.create_object(id=self.m1_id, category="ENDPOINT", version="2")
        self.m1_2['return_type_spec'] = schema.get("result_endpoint").schema
        #self.m1_2['license_end'] = time.mktime(time.strptime("2016 06 30 0 0 0", "%Y %m %d %H %M %S"))

        self.my_models.append(self.m1_2)

        """
        define a categorical return type
        """
        self.m2_id = '/Sample Path/Other Sample Model/1'
        self.m2_1 = calculation_info.create_object(id=self.m2_id, category="ENDPOINT", version="1")

        ac_lic_info = {
            'license_end': time.mktime(time.strptime("2016 06 30 0 0 0", "%Y %m %d %H %M %S")),
            'license_info': 'AdrianaCode 2.6 community edition'
        }
 
        self.m2_1['license_infos'] = [ ac_lic_info, ]

        r_type = schema.get("result_endpoint").schema
        r_type['properties']['value'] = { "enum": ["positive", "negative", "unknown"]}

        self.m2_1['return_type_spec'] = r_type

        self.my_models.append(self.m2_1)
