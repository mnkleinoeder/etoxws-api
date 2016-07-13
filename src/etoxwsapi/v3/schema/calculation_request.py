
calculation_request =  {
		"type": "object",
		"properties": {
			"req_calculations" : {
				"type": "array",
				"items": {
					"type": "object",
					#"$ref": "http://etoxsys.eu/schema/etoxws/v3/calculation_info#" },
					"description": "calculation_info objects as obtained from /dir"
				} 
			},
			"sdf_file": {
				"type": "string",
				"description": "input structure as string in SDFile format"
			}
		},
		#"required": [ "req_predictions", "sdf_file" ] ,
		"additionalProperties": False,
	}

