
metabolite = {
	"type": "object",
	"properties": {
		"structure" : {
			"type": "string",
			"description": "SDFile record representing a metabolite"
		},
		"probability": {
			"type": "number",
			"description": ""
		}
	},
	"additionalProperties": False,
}
result_metabolism =	{
	"type": "object",
	"properties": {
		"cmp_id" : { "type": "string" },
		"result" : {
			"type": "array",
 			"items": {
				"type": "object",
				"description": "metabolites as described by the metabolite schema",
				#"$ref": "http://etoxsys.eu/schema/etoxws/v2/metabolite#" },
 			},
		},
	},
	"required": [ "result" ],
	"additionalProperties": False,
}

