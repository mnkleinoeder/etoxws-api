# encoding: utf-8

import sys
import os

import requests
import time
from etoxwsapi.v2 import schema
import json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = 'http://localhost/etoxwsapi/v2'

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
		
		job_ids = list()
		for stat in json.loads(req_ret.text):
			job_ids.append(stat['job_id'])
			print "======================================================================"
			print "new job submitted."
			for t in ("job_id", "status", "msg"):
				print "%s: %s"%(t, stat[t])

		print "observing running jobs for 10sec. (or until one is completed)"
		do_poll = True
		while do_poll:
			do_poll = False
			for job_id in job_ids:
				response = requests.get(BASE_URL+"/jobs/%s"%(job_id))
				if response.status_code == 200:
					do_poll = True
					stat = json.loads(response.text)
					print "status for '%s': %s"%(job_id, stat)
					if stat['status'] == "JOB_COMPLETED":
						print "Job completed. Done."
						do_poll = False
				else:
					print response.status_code
					print response.text
			time.sleep(1)

	except Exception, e:
		print e
		return 1
	return 0

if __name__ == "__main__":
	sys.exit(main())