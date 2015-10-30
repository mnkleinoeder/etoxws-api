"""
Dummy program for simulating CORINA run with output to stdout
"""

import sys
import os
import time
import re
from StringIO import StringIO

out_str = """
*** RECORD no.: %(nr)s read ***********************
   Name mol%(nr)s
   45 atoms
   Elapsed time: 10 ms
"""

SLEEP_TIME = 3

def main(argv):
    #raise Exception("failed by purpose")
    property = sys.argv[1]
    version = sys.argv[2]
    infile = sys.argv[3]
    outfile = sys.argv[4]

    ifp = open(infile)
    ofp = open(outfile, "w")

    i = 0
    for lno, line in enumerate(ifp):
        if '$$$$' in line:
            i += 1
            sys.stdout.write(out_str%{"nr": i})
            sys.stdout.flush()
            print >>ofp, "\t".join((str(len(property)), "0.8", "0.9"))
            time.sleep(SLEEP_TIME)
    print "stop"


main(sys.argv)

if __name__ == '__main__':
    regex = re.compile("\*\*\* RECORD no\.:\s+(\d+)\s+read \*")

    s = StringIO(out_str%{"nr":99})
    for line in s:
        m = regex.search(line)
        if not m:
            continue
        print m.group(1)
