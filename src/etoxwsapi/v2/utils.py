import hashlib
import logging

def create_value_type_spec(spec):
	return	{
		"name": "value_type_spec",
		"type": "object",
		"properties": {
			"value" : spec,
		},
		"additionalProperties": False,
	}

def modelid_from_calcinfo(calc_info):
	return modelid(*([calc_info.get(key, None) for key in ('modeltag', 'partner', 'version')]))

def modelid(mtaxonomy, mprovider, mversion):
	'''
	as eTOXvault has no logical unique id per model in the DB design a hash is generated from the 
	key logical entries in the record. Both a human readable tag and a hashed id is returned.
	
	returns tuple: (tag, hashid)
	'''
	mtag = None
	try:
		if mtaxonomy and mprovider and mversion:
			# very ugly hack to rectify wrong provider string
			_p = mprovider
			if mprovider == "Inte:Ligand GmbH":
				_p = 'IL'
			# making the clunky version info in etoxvault more tolerant
			_v = int(float(mversion))

			mtag = ':'.join([str(val).strip() for val in (mtaxonomy, _p, _v)])
	except Exception, e:
		logging.debug("Could not generate modelid %s"%(e))
	mid = hashlib.md5(str(mtag)).hexdigest()
	ret = (mtag, mid)
	return ret 