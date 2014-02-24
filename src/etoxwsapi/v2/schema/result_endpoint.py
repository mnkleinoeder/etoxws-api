

result_endpoint =	{
	"type": "object",
	"properties": {
		"cmp_id" : { "type": "string" },
		"value" :{
			"type": "number",
			"description": "the type should be redefined if needed"
		},
		"AD" : {
			"type":	"number",
			"minimum": 0,
			"minimum": 1
		},
		"RI" : { "type": "number" },
		"msg": { "type": "string" }
	},
	#"required": [ "result" ],
	"additionalProperties": False,
}

