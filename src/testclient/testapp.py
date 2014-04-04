# encoding: utf-8

import sys
import os

import requests
import time
from etoxwsapi.v2 import schema
import json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = 'http://localhost:8000/etoxwsapi/v2'
#BASE_URL = 'http://localhost/etoxwsapi/v2'
#BASE_URL = 'http://192.168.178.217/etoxwsapi/v2'

def print_result(ids):
	frmt = '| %-7s | %-10s | %-10s | %-10s |'
	for (job_id,model_id) in ids:
		ret = requests.get('/'.join((BASE_URL, 'jobs', job_id)))
		if ret.status_code == 200:
			results = json.loads(ret.text)
			print "==========================================================================="
			print "Results for model '%s' (job: %s)\n"%(model_id, job_id)
			print frmt%("cmp_id", "value", "AD", "RI")
			print '-' * len(frmt%('','','',''))
			for r in results['results']:
				print frmt%(r['cmp_id'], r['value'], r['AD']['value'], r['RI']['value'])

def main(argv=None):
	try:
		ret = requests.get(BASE_URL+"/dir")
		print ret.status_code
		models = [ m for m in json.loads(ret.text)]
		
		model_ids = [ model['id'] for model in models ]

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
		
		if req_ret.status_code == 200:
			job_ids = list()
			for stat in json.loads(req_ret.text):
				job_ids.append(stat['job_id'])
				print "======================================================================"
				print "new job submitted."
				for t in ("job_id", "status"): #, "msg"):
					print "%s: %s"%(t, stat[t])

			observe_time = 10
			print "observing running jobs for %dsec. (or until one is completed)"%(observe_time)
			for i in range(observe_time):
				done = True
				for job_id in job_ids:
					response = requests.get(BASE_URL+"/jobs/%s"%(job_id))
					if response.status_code == 200:
						done = False
						stat = json.loads(response.text)
						print "status for '%s': %s"%(job_id, stat)
						if stat['status'] != "JOB_RUNNING":
							print "Job not running anymore."
							done = True
					else:
						print response.status_code
						print response.text
				time.sleep(1)
				if done:
					break
		else:
			print "Error occurred (%s)"%(req_ret.status_code)
			print req_ret.text

		print_result(zip(job_ids, model_ids) )

	except Exception, e:
		print "Error occured: %s"%(e)
		return 1
	return 0

if __name__ == "__main__":
	sys.exit(main())