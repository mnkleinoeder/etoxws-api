
import json
import jsonschema
import warlock
import copy
import os
import glob
import re
import types
import logging

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
	id_base =	"http://etoxsys.eu/schema/etoxws/v2/%(name)s#"
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

def _get_registry():
	global _registry
	if _registry:
		return _registry
	dir_impl = os.path.dirname(os.path.abspath(__file__))
	_registry = dict()
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
						if _registry.has_key(var_name):
							logging.warn("schema ")
						_registry[var_name] = SchemaDefinition(name=var_name, schema=var)
						logging.debug("Imported schema: %s.%s"%(module_name, var_name))
					except Exception, ee:
						logging.warn("Could not create schema from dict '%s.%s': %s"%(module_name, var_name, ee))
		except Exception, e:
			logging.warn("Error while trying to import '%s': %s"%(module_name, e))
	return _registry
	

def get(name):
	registry = _get_registry()
	if registry.has_key(name):
		return registry.get(name)
	else:
		raise LookupError("Schema '%s' not available"%(name))

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	print get('ws_info')
	print _registry.keys()


	