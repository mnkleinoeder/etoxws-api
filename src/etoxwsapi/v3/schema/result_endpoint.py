

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
			"description": "applicability domain assessment ADAN",
			"type":	"object",
			"properties": {
				"value": {
					"type": "number",
					"minimum": 0,
					"maximum": 6,
				},
				"success": { "type": "boolean" },
				"message": { "type": "string" },
			},
			"required": [ "success" ],
			"additionalProperties": False,
		},
		"RI" : {
			"description": "reliability index measure",
			"type":	"object",
			"properties": {
				"value": { "type": "number" },
				"success": { "type": "boolean" },
				"message": { "type": "string" },
			},
			"required": [ "success" ],
			"additionalProperties": False,
		},
	},
	#"required": [ "result" ],
	"additionalProperties": False,
}

