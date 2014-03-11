

result_endpoint =	{
	"type": "object",
	"properties": {
		"cmp_id" : { "type": "string" },
		"value" :{
			"type": "number",
			"description": "the type should be redefined if needed"
		},
		"success": { "type": "boolean" },
		"message": { "type": "string" },
		"AD" : {
			"type":	"object",
			"properties": {
				"value": {
					"type": "number",
					"minimum": 0,
					"minimum": 6,
				},
				"success": { "type": "boolean" },
				"message": { "type": "string" },
			},
			"additionalProperties": False,
		},
		"RI" : {
			"type":	"object",
			"properties": {
				"value": { "type": "number" },
				"success": { "type": "boolean" },
				"message": { "type": "string" },
			},
			"additionalProperties": False,
		},
	},
	#"required": [ "result" ],
	"additionalProperties": False,
}

