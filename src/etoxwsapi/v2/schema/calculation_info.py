
control_parameter_info = 	{
		"type": "object",
		"properties": {
			"name" : { "type": "string" },
			"display_name" : { "type": "string" },
			"data_type" : { "enum": ["integer", "number", "string"] },
			"description":  { "type": "string" }
		},
		#"required": [ "name", "display_name", "data_type" ] ,
		"additionalProperties": False,
	}

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
				"items": { "$ref": "http://etoxsys.eu/schema/etoxws/v2/control_parameter_info#" },
			},
			"return_type_spec": {
				"type": "object",
				"description": "JSON schema for specifying the return data"
			}
		},
		"required": [ "id", "category" ] ,
		"additionalProperties": False,
	}

