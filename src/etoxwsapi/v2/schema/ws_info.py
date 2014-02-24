
ws_info =	{
	"type": "object",
	"properties": {
		"provider" : { "type": "string" },
		"homepage" : { "type": "string" },
		"admin" : { "type": "string" },
		"admin_email" : {
			"type": "string",
			#"pattern": "^[\w\.]+@[\w\.]+$"
			"pattern": "[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}"
		},
	},
	"required": [ "provider", "admin_email"],
	"additionalProperties": False,
}

