"""
job_status objects are used to report the status after submission and to track the
status during execution of a job
"""

job_status =	{
	"type": "object",
	"properties": {
		"job_id" : { "type": "string" },
 		"status" : {
 			"enum": [
				"JOB_UNKNOWN",
 				"JOB_REJECTED",
 				"JOB_ACCEPTED",
 				"JOB_RUNNING",
 				"JOB_COMPLETED",
 				"JOB_FAILED",
 				"JOB_CANCELLED"
 			],
			#"default": "JOB_UNKNOWN"
		},
		"start_time": { "type": "number" },
		"completion_time": { "type": "number" },
		"nrecord": { "type": "integer" },
		"currecord": { "type": "integer" },
		"calculation_info" : {
			"type": "object",
			#"$ref": "http://etoxsys.eu/schema/etoxws/v2/calculation_info#",
		},
		"results": {
			"type" : "array",
			"items": {
				"type": "object",
				"description": "instance of a result type matching the return_type_spec in the calculation_info"
			}
		},
		"msg" : { "type": "string" },
	},
	#"additionalProperties": False,
}

_job_status_doc = """
"""
