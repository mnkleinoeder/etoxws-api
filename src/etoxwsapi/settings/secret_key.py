'''
Created on 25.03.2014

@author: thomas
'''
import string, random
import os
string.printable

try:
	from _secret_key import SECRET_KEY
except ImportError:
	SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
	SECRET_KEY = ''.join([random.choice(string.letters+string.digits) for n in xrange(64)])
	with open(os.path.join(SETTINGS_DIR, '_secret_key.py'), 'wb') as fp:
		print >>fp, "SECRET_KEY='%s'"%(SECRET_KEY)
