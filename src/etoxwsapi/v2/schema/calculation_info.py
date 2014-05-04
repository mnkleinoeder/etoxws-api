"""
calculation_info is used to define a calculation method that a webservice provides

Please note the member ``return_type_spec`` in the schema definition. This member is required
for defining the return type of the calculation. This is illustrated in the following code
fragment.

::

	from etoxwsapi.v2 import schema

	self.dipl_id = '/Tox/Organ Tox/Phospholipidosis/DIPL/1'
	self.dipl_1 = calculation_info.create_object(id=self.dipl_id, category="ENDPOINT", external_id = "eTOXvault ID2")
	r_type = schema.get("result_endpoint").schema
	r_type['properties']['value'] = { "enum": ["positive", "negative", "unknown"]}
	self.dipl_1['return_type_spec'] = r_type

"""

calculation_info =  {
		"type": "object",
		"properties": {
			"category": {
				"enum": [
					"ENDPOINT",
					"METABOLISM",
				]
			},
			"id" : { 
						"type": "string",
						"pattern": "^(/[^/]+)+/\d+$",
						"description": "'/' separated hierarchical description, eg. '/Toxicity/Organ Toxicity/Phospholipidosis/DIPL/1'"
			},
			"external_id" : { 
							"type": "string",
							"description": "reference to meta data repository (eTOXvault)."
			},
			"control_parameter_infos" : {
				"type": "array",
				# how to implement validation of embedded types?
				"items": { "$ref": "http://etoxsys.eu/etoxwsapi/v2/schema/control_parameter_info#" },
			},
			"return_type_spec": {
				"type": "object",
				"description": "JSON schema for specifying the return data"
			}
		},
		"required": [ "id", "category" ] ,
		"additionalProperties": False,
	}

