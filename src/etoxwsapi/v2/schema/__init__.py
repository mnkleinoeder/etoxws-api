
import json
import jsonschema
import warlock
import copy
import os
import glob
import re
import types
import logging
from pprint import pprint
from warlock.core import model_factory

class Model(warlock.model.Model):
    def to_json(self, indent=None):
        return json.dumps(self, indent=indent)

    # TODO: implement __deepcopy__
    # needs to be copied in order to correctly create objects
    # with multiple required properties in the corresponding schema
# 	def __deepcopy__(self, memo):
# 		pass

class SchemaDefinition(object):
    '''
    classdocs
    '''
    id_base =	"http://etoxsys.eu/etoxwsapi/v2/schema/%(name)s#"
    schema_version = "http://json-schema.org/draft-04/schema#"

    def __init__(self, name, schema):
        self.name = name
        self.schema = copy.deepcopy(schema)
        #print "%(name)s"%{'name': name}
        self.schema.update({"name": name, "id": self.id_base%{'name': name}, "$schema": self.schema_version})
        self.kls = warlock.model_factory(self.schema, base_class=Model)

    def create_object(self, **kwargs):
        return self.kls(**kwargs)

    def to_json(self, **kwargs):
        return json.dumps(self.schema, **kwargs)

    def validate(self, jsondata):
        if not isinstance(jsondata, types.DictType):
            raise TypeError("object to be validated must have dict type")
        jsonschema.validate(jsondata, self.schema)

    def loads(self, s, **kwargs):
        '''
        converts s using json and validates obtained object
        '''
        o = json.loads(s, **kwargs)
        if isinstance(o, types.ListType):
            for oo in o:
                self.validate(oo)
        return o

_registry = None
_documentation = None

def get_registry():
    _init_registry()
    return _registry

def _init_registry():
    global _registry, _documentation

    if _registry:
        return

    dir_impl = os.path.dirname(os.path.abspath(__file__))
    _registry = dict()
    _documentation = dict()
    name_re = re.compile('^([a-z][_a-zA-Z]+)\.py$')
    flist = [ f for f in os.listdir(dir_impl) if f.endswith('.py') ]
    for name in flist :
        m = name_re.match(name)
        if not m:
            continue
        module_name = m.group(1)
        try:
            mod = __import__('etoxwsapi.v2.schema.%s'%(module_name), fromlist=['etoxwsapi.v2.schema'])
            for var_name in [ v for v in dir(mod) if not v.startswith('_') ]:
                var = getattr(mod, var_name)
                if isinstance(var, types.DictType) and var.has_key('type'):
                    try:
                        _registry[var_name] = SchemaDefinition(name=var_name, schema=var)
                        _documentation[var_name] = mod.__doc__
                        logging.debug("Imported schema: %s.%s"%(module_name, var_name))
                    except Exception, ee:
                        logging.warn("Could not create schema from dict '%s.%s': %s"%(module_name, var_name, ee))
        except Exception, e:
            logging.warn("Error while trying to import '%s': %s"%(module_name, e))

def get(name):
    registry = get_registry()
    if registry.has_key(name):
        return registry.get(name)
    else:
        raise LookupError("Schema '%s' not available"%(name))

def get_doc(name):
    get_registry()
    if _documentation.has_key(name):
        return _documentation.get(name) or "No documentation available"
    else:
        raise LookupError("Schema '%s' not available"%(name))

def urlconf():
    from django.conf.urls import url
    from django.http.response import HttpResponse
    urls = list()
    registry = get_registry()
    for name, schema in registry.iteritems():
        class _View:
            def __init__(self, schema):
                self.schema = schema
            def __call__(self, request):
                jsondata = self.schema.to_json(indent=2)
                return HttpResponse(jsondata, content_type='application/json')
        urls.append(url(r'%s$'%(name),  _View(schema), name='schema_%s'%(name)))

    return urls

def create_result_endpoint(data_type):
    """
    helper function to create custom return types
    """
    if data_type not in ('array', 'boolean', 'integer', 'number', 'object', 'string'):
        raise TypeError("data_type '%s' is not allowed in JSON schema"%(data_type))
    from etoxwsapi.v2.schema import result_endpoint
    #rs = copy.deepcopy(result_endpoint.result_endpoint)
    rs = copy.deepcopy(result_endpoint.result_endpoint)
    rs['properties']['value']['type'] = data_type
    return SchemaDefinition("result_endpoint"+data_type, rs)

def validate(obj, sm):
    """
    helper to validate and return the same object
    """
    sm.validate(obj)
    return obj


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_info = get('ws_info')
    print type(ws_info.schema)
    print ws_info.to_json()
#	print get_doc('ws_info')

    rs_string = create_result_endpoint('string').schema
    print rs_string['properties']['value']['type']
    t = SchemaDefinition('tmp', rs_string).create_object()
    t['bla'] = 'bla'
    
