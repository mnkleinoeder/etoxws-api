#!/usr/bin/env python

import os

from etoxwsapi.v2.schema import get_registry, get_doc

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

tmp_dir = os.path.join(THIS_DIR, 'build')

with open(os.path.join(tmp_dir, 'data_types.rst'), 'w') as summary_fp:

	for name, schema in get_registry().iteritems():
		print >>summary_fp
		print >>summary_fp, "%s\n%s"%(name, '~'*len(name))
		print >>summary_fp
		print >>summary_fp, get_doc(name)
		print >>summary_fp
		print >>summary_fp, "Schema"
		print >>summary_fp, "......"
		print >>summary_fp
		print >>summary_fp,	"::"
		print >>summary_fp
		for l in schema.to_json(indent=2).split('\n'):
			print >>summary_fp, "  %s"%(l)
		print >>summary_fp

# 		fname = os.path.join(tmp_dir, '%s.schema.rst'%(name))
# 		with open(fname, 'w') as fp:
# 			print >>fp, schema.to_json(indent=2)
# 		fname = os.path.join(tmp_dir, '%s.doc.rst'%(name))
# 		with open(fname, 'w') as fp:
# 			print >>fp, get_doc(name)
