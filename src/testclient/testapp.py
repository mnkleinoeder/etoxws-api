# encoding: utf-8

import sys
import os

import requests
import time
from etoxwsapi.v2 import schema
import json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = 'http://localhost:8000/etoxwsapi/v2'

def main(argv=None):
	try:
		ret = requests.get(BASE_URL+"/dir")
		models = [ m for m in json.loads(ret.text)]

		print "Available models"
		print models

		print "All jobs:"
		ret = requests.get(BASE_URL+"/jobs/")
		print ret.text

		"""
		preparing request for calculation
		"""
		calculation_request = schema.get('calculation_request')
		req_obj = calculation_request.create_object()

		calculation_info = schema.get('calculation_info')
		
		req_obj.req_calculations = models

		fname = os.path.join(THIS_DIR, "tiny.sdf")
		with open(fname) as fp:
			req_obj.sdf_file = fp.read()

		req_ret = requests.post(BASE_URL+"/jobs/", data = req_obj.to_json())
		
		job_ids = [ stat['job_id'] for stat in json.loads(req_ret.text) ]
		for job_id in job_ids:
			print "new job submitted. job_id is: %s"%(job_id)

		print "observing running jobs for 10sec. (or until one is completed)"
		do_poll = True
		while do_poll:
			for job_id in job_ids:
				stat = json.loads(requests.get(BASE_URL+"/jobs/%s"%(job_id)).text)
				print "status for '%s': %s"%(job_id, stat)
				if stat['status'] == "JOB_COMPLETED":
					print "Job completed. Done."
					do_poll = False
			time.sleep(1)

	except Exception, e:
		print e
		return 1
	return 0

if __name__ == "__main__":
	sys.exit(main())