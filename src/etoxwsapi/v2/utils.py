
def create_value_type_spec(spec):
	return	{
		"name": "value_type_spec",
		"type": "object",
		"properties": {
			"value" : spec,
		},
		"additionalProperties": False,
	}

