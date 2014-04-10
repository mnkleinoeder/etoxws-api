'''
Created on 03.04.2014

@author: thomas
'''

class DisableCSRF(object):
	def process_request(self, request):
		setattr(request, '_dont_enforce_csrf_checks', True)