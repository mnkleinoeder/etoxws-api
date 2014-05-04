"""
"""

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

